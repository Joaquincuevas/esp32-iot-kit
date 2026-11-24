# Changelog

[Leer en español](docs/es/CHANGELOG.md)

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] - 2026-11-24

### Added

- The firmware stops with a clear `[config]` message when `config.h` still has the example credentials.
- Bridge tests for reconnection (re-subscribing), refused credentials, dropped messages and the InfluxDB write.
- Mosquitto and the bridge refuse to start, with a clear message, when a value keeps the `change-me` prefix from `.env.example`.
- CI job that validates the Docker Compose file with `.env.example` and runs the Mosquitto entrypoint shell test.

### Changed

- The bridge reports every missing environment variable at once and validates `MQTT_PORT`, instead of failing on the first one or with a traceback.
- `docker compose up` without `.env` says to copy `.env.example` instead of showing a path error.
- The documentation (hardware, troubleshooting, CONTRIBUTING and CHANGELOG) is now in English; the Spanish versions are in `docs/es/`.

## [0.1.0] - 2026-11-03

### Added

- ESP32 firmware (PlatformIO, Arduino): DHT22 reading with a configurable interval and JSON publishing to `devices/{device_id}/telemetry`.
- WiFi and MQTT reconnection with exponential backoff (1 s to 60 s).
- NTP timestamp; without synchronization, the message is sent without `ts`.
- Temperature and humidity calibration offsets.
- Python 3.12 MQTT-to-InfluxDB 2 bridge with message validation, reconnection and pytest tests.
- Docker Compose with Mosquitto (mandatory authentication), InfluxDB 2, Grafana and the bridge.
- Grafana with an automatically provisioned datasource and a temperature and humidity dashboard per device.
- Hardware and troubleshooting documentation, and CI with GitHub Actions.

[Unreleased]: https://github.com/joaquincuevas/esp32-iot-kit/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/joaquincuevas/esp32-iot-kit/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/joaquincuevas/esp32-iot-kit/releases/tag/v0.1.0
