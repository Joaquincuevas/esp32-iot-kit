from types import SimpleNamespace

import pytest

from bridge import Bridge, ConfigError, load_config, parse_message

TOPIC = "devices/esp32-01/telemetry"
NOW = 1762171200


def test_with_ts():
    r = parse_message(TOPIC, b'{"temperature":23.4,"humidity":45.1,"ts":1762170000}', NOW)
    assert r == {"device_id": "esp32-01", "temperature": 23.4, "humidity": 45.1, "ts": 1762170000}


def test_without_ts_uses_receive_time():
    r = parse_message(TOPIC, b'{"temperature":23,"humidity":45}', NOW)
    assert r["ts"] == NOW
    assert r["temperature"] == 23.0


@pytest.mark.parametrize("payload", [b"not json", b"\xff\xfe", b"[1,2]", b""])
def test_invalid_json(payload):
    with pytest.raises(ValueError):
        parse_message(TOPIC, payload, NOW)


@pytest.mark.parametrize(
    "payload",
    [
        b'{"temperature":81,"humidity":45}',
        b'{"temperature":-41,"humidity":45}',
        b'{"temperature":23,"humidity":100.1}',
        b'{"temperature":23,"humidity":-1}',
    ],
)
def test_out_of_range(payload):
    with pytest.raises(ValueError, match="outside"):
        parse_message(TOPIC, payload, NOW)


@pytest.mark.parametrize(
    "payload",
    [
        b'{"humidity":45}',
        b'{"temperature":"23","humidity":45}',
        b'{"temperature":true,"humidity":45}',
        b'{"temperature":23,"humidity":45,"ts":"1762170000"}',
        b'{"temperature":23,"humidity":45,"ts":-5}',
    ],
)
def test_bad_fields(payload):
    with pytest.raises(ValueError):
        parse_message(TOPIC, payload, NOW)


@pytest.mark.parametrize("topic", ["devices//telemetry", "devices/a/b/telemetry", "other/a/telemetry"])
def test_bad_topic(topic):
    with pytest.raises(ValueError, match="topic"):
        parse_message(topic, b'{"temperature":23,"humidity":45}', NOW)


# --- configuration -----------------------------------------------------------

FULL_ENV = {
    "MQTT_HOST": "mosquitto",
    "MQTT_USER": "esp32",
    "MQTT_PASSWORD": "x",
    "INFLUX_URL": "http://influxdb:8086",
    "INFLUX_TOKEN": "t",
    "INFLUX_ORG": "o",
    "INFLUX_BUCKET": "b",
}


def test_config_defaults_port():
    assert load_config(FULL_ENV)["MQTT_PORT"] == 1883


def test_config_reports_all_missing_variables():
    with pytest.raises(ConfigError) as exc:
        load_config({"MQTT_HOST": "h", "INFLUX_URL": ""})
    message = str(exc.value)
    for name in ("MQTT_USER", "MQTT_PASSWORD", "INFLUX_URL", "INFLUX_TOKEN", "INFLUX_ORG", "INFLUX_BUCKET"):
        assert name in message
    assert "MQTT_HOST" not in message
    assert ".env.example" in message


def test_config_rejects_bad_port():
    with pytest.raises(ConfigError, match="MQTT_PORT"):
        load_config({**FULL_ENV, "MQTT_PORT": "abc"})


# --- MQTT callbacks (no broker needed) ---------------------------------------


class Reason:
    def __init__(self, failure):
        self.is_failure = failure

    def __str__(self):
        return "Not authorized" if self.is_failure else "Success"


class FakeClient:
    def __init__(self):
        self.subscriptions = []

    def subscribe(self, topic, qos=0):
        self.subscriptions.append((topic, qos))


class FakeWriteApi:
    def __init__(self):
        self.records = []

    def write(self, bucket, record):
        self.records.append((bucket, record))


@pytest.fixture
def handlers():
    return Bridge(FakeWriteApi(), "telemetry")


def test_subscribes_again_after_every_reconnect(handlers):
    client = FakeClient()
    handlers.on_connect(client, None, None, Reason(False), None)
    handlers.on_disconnect(client, None, None, 7, None)  # connection lost, paho reconnects by itself
    handlers.on_connect(client, None, None, Reason(False), None)
    assert client.subscriptions == [("devices/+/telemetry", 1)] * 2


def test_refused_connection_does_not_subscribe(handlers, caplog):
    client = FakeClient()
    with caplog.at_level("ERROR", logger="bridge"):
        handlers.on_connect(client, None, None, Reason(True), None)
    assert client.subscriptions == []
    assert "MQTT_USER" in caplog.text


def test_unexpected_disconnect_is_logged(handlers, caplog):
    with caplog.at_level("WARNING", logger="bridge"):
        handlers.on_disconnect(FakeClient(), None, None, 7, None)
    assert "reconnecting" in caplog.text


def test_valid_message_is_written(handlers):
    msg = SimpleNamespace(topic=TOPIC, payload=b'{"temperature":23.4,"humidity":45.1,"ts":1762170000}')
    handlers.on_message(None, None, msg)
    assert len(handlers.write_api.records) == 1
    bucket, point = handlers.write_api.records[0]
    assert bucket == "telemetry"
    line = point.to_line_protocol()
    assert line.startswith("climate,device_id=esp32-01 ")
    assert "temperature=23.4" in line and "humidity=45.1" in line


def test_invalid_message_is_dropped_not_fatal(handlers, caplog):
    msg = SimpleNamespace(topic=TOPIC, payload=b"not json")
    with caplog.at_level("WARNING", logger="bridge"):
        handlers.on_message(None, None, msg)
    assert handlers.write_api.records == []
    assert "Dropped message" in caplog.text
