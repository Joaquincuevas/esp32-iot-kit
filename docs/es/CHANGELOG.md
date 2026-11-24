# Changelog

[Read in English](../../CHANGELOG.md)

Todos los cambios relevantes de este proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added

- El firmware se detiene con un mensaje `[config]` claro si `config.h` conserva las credenciales de ejemplo.
- Tests del bridge para la reconexión (re-suscripción), credenciales rechazadas, mensajes descartados y la escritura a InfluxDB.
- Job de CI que valida el archivo de Docker Compose con `.env.example` y ejecuta el test de shell del entrypoint de Mosquitto.
- Mosquitto y el bridge se niegan a arrancar si un valor conserva el prefijo `change-me` de `.env.example`, con un mensaje claro.

### Changed

- El bridge informa de una sola vez todas las variables de entorno que faltan y valida `MQTT_PORT`, en lugar de fallar con la primera o con un traceback.
- `docker compose up` sin `.env` indica copiar `.env.example` en lugar de un error de ruta.
- La documentación (hardware, troubleshooting, CONTRIBUTING y CHANGELOG) está en inglés; las versiones en español están en `docs/es/`.

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
