import pytest

from bridge import parse_message

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
