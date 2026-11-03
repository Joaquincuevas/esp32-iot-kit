# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

## [0.1.0] - 2026-11-03

### Added

- Firmware ESP32 (PlatformIO, Arduino): lectura de DHT22 con intervalo configurable y publicación JSON en `devices/{device_id}/telemetry`.
- Reconexión WiFi y MQTT con backoff exponencial (1 s a 60 s).
- Timestamp por NTP; si no hay sincronización, el mensaje se envía sin `ts`.
- Offsets de calibración de temperatura y humedad.
- Bridge Python 3.12 de MQTT a InfluxDB 2 con validación de mensajes, reconexión y tests con pytest.
- Docker Compose con Mosquitto (autenticación obligatoria), InfluxDB 2, Grafana y el bridge.
- Grafana con datasource y dashboard de temperatura y humedad por dispositivo provisionados automáticamente.
- Documentación de hardware y troubleshooting, y CI con GitHub Actions.

[Unreleased]: https://github.com/joaquincuevas/esp32-iot-kit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/joaquincuevas/esp32-iot-kit/releases/tag/v0.1.0
