"""MQTT -> InfluxDB 2 bridge for esp32-iot-kit telemetry."""

import json
import logging
import os
import signal
import sys
import time

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WriteOptions, WritePrecision

TOPIC = "devices/+/telemetry"
MEASUREMENT = "climate"
# DHT22 datasheet limits; anything outside is a wiring or sensor fault.
TEMP_RANGE = (-40.0, 80.0)
HUMIDITY_RANGE = (0.0, 100.0)

REQUIRED_ENV = (
    "MQTT_HOST",
    "MQTT_USER",
    "MQTT_PASSWORD",
    "INFLUX_URL",
    "INFLUX_TOKEN",
    "INFLUX_ORG",
    "INFLUX_BUCKET",
)

log = logging.getLogger("bridge")


def parse_message(topic, payload, received_at):
    """Return a reading dict or raise ValueError describing why the message was rejected."""
    parts = topic.split("/")
    if len(parts) != 3 or parts[0] != "devices" or parts[2] != "telemetry" or not parts[1]:
        raise ValueError(f"unexpected topic {topic!r}")

    try:
        data = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"invalid JSON: {e}") from None
    if not isinstance(data, dict):
        raise ValueError("payload is not a JSON object")

    reading = {"device_id": parts[1]}
    for field, (lo, hi) in (("temperature", TEMP_RANGE), ("humidity", HUMIDITY_RANGE)):
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} missing or not a number: {value!r}")
        if not lo <= value <= hi:
            raise ValueError(f"{field}={value} outside [{lo}, {hi}]")
        reading[field] = float(value)

    ts = data.get("ts")
    if ts is None:
        ts = received_at
    elif isinstance(ts, bool) or not isinstance(ts, int) or ts <= 0:
        raise ValueError(f"ts must be a positive integer epoch in seconds: {ts!r}")
    reading["ts"] = ts
    return reading


class ConfigError(Exception):
    pass


def load_config(environ):
    """Read settings from the environment, reporting every problem at once."""
    missing = [name for name in REQUIRED_ENV if not environ.get(name)]
    if missing:
        raise ConfigError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". With Docker Compose, copy .env.example to .env and fill it in."
        )
    config = {name: environ[name] for name in REQUIRED_ENV}
    raw_port = environ.get("MQTT_PORT") or "1883"
    try:
        config["MQTT_PORT"] = int(raw_port)
    except ValueError:
        raise ConfigError(f"MQTT_PORT must be an integer, got {raw_port!r}") from None
    return config


class Bridge:
    """MQTT callbacks, kept apart from main() so they can be tested without a broker."""

    def __init__(self, write_api, bucket):
        self.write_api = write_api
        self.bucket = bucket

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            log.error("MQTT connection refused: %s (check MQTT_USER and MQTT_PASSWORD)", reason_code)
            return
        # Subscribing here, not once at startup, restores the subscription after every reconnect.
        log.info("MQTT connected, subscribing to %s", TOPIC)
        client.subscribe(TOPIC, qos=1)

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            log.warning("MQTT disconnected (%s), reconnecting", reason_code)

    def on_message(self, client, userdata, msg):
        try:
            r = parse_message(msg.topic, msg.payload, int(time.time()))
        except ValueError as e:
            log.warning("Dropped message on %s: %s", msg.topic, e)
            return
        point = (
            Point(MEASUREMENT)
            .tag("device_id", r["device_id"])
            .field("temperature", r["temperature"])
            .field("humidity", r["humidity"])
            .time(r["ts"], WritePrecision.S)
        )
        self.write_api.write(bucket=self.bucket, record=point)
        log.info("%s temperature=%.2f humidity=%.2f ts=%d", r["device_id"], r["temperature"], r["humidity"], r["ts"])


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    try:
        config = load_config(os.environ)
    except ConfigError as e:
        sys.exit(str(e))

    influx = InfluxDBClient(url=config["INFLUX_URL"], token=config["INFLUX_TOKEN"], org=config["INFLUX_ORG"])
    # Batching mode retries failed writes with backoff, so a short InfluxDB outage loses nothing.
    write_api = influx.write_api(
        write_options=WriteOptions(batch_size=100, flush_interval=1_000),
        error_callback=lambda conf, data, err: log.error("InfluxDB write failed: %s", err),
        retry_callback=lambda conf, data, err: log.warning("InfluxDB write retry: %s", err),
    )
    handlers = Bridge(write_api, config["INFLUX_BUCKET"])

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="esp32-iot-kit-bridge")
    client.username_pw_set(config["MQTT_USER"], config["MQTT_PASSWORD"])
    client.on_connect = handlers.on_connect
    client.on_disconnect = handlers.on_disconnect
    client.on_message = handlers.on_message
    client.reconnect_delay_set(min_delay=1, max_delay=60)

    signal.signal(signal.SIGTERM, lambda *_: client.disconnect())

    host, port = config["MQTT_HOST"], config["MQTT_PORT"]
    log.info("Connecting to MQTT %s:%d", host, port)
    client.connect_async(host, port)
    try:
        client.loop_forever(retry_first_connection=True)
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Shutting down, flushing pending writes")
        write_api.close()
        influx.close()


if __name__ == "__main__":
    main()
