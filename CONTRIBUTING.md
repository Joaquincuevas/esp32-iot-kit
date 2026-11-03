# Contribuir

Gracias por tu interés. Esta plantilla prioriza ser **clara y fácil de usar**: un cambio que la vuelva más difícil de entender necesita una muy buena razón.

## Antes de empezar

- Para bugs, abre un issue con: placa, versión del repo, log serie (`pio device monitor`) y/o `docker compose logs bridge`. **Borra contraseñas y tokens** antes de pegar logs.
- Para funcionalidades nuevas, abre primero un issue para conversarlo; revisa el [Roadmap](README.md#roadmap).

## Entorno de desarrollo

```bash
# Firmware: debe compilar sin config.h (usa config.example.h)
cd firmware && pio run

# Bridge: tests con Python 3.12
cd bridge && pip install -r requirements.txt pytest && pytest -q
# o sin Python 3.12 local:
docker run --rm -v "$PWD/bridge:/app" -w /app python:3.12 sh -c "pip install -r requirements.txt pytest && pytest -q"

# Stack completo
cp .env.example .env && docker compose up -d
```

## Pull requests

1. Crea una rama desde `main`.
2. Mantén el PR enfocado en un solo cambio.
3. Si cambias el formato del mensaje MQTT, actualiza `parse_message` en el bridge, sus tests y el README.
4. Si cambias configuración, actualiza `config.example.h` o `.env.example` y la tabla del README.
5. Añade una entrada en la sección `Unreleased` de [CHANGELOG.md](CHANGELOG.md).
6. CI (`pio run` + `pytest`) debe pasar.

## Estilo

- **Firmware:** C++ del framework Arduino, sin dependencias nuevas si unas pocas líneas bastan. Comenta el *por qué*, no el *qué*.
- **Bridge:** Python 3.12, solo librería estándar más `paho-mqtt` e `influxdb-client`. Configuración únicamente por variables de entorno.
- **Secretos:** nunca en el código ni en commits. Usa placeholders en los archivos `*.example`.
- **Commits:** en inglés y en imperativo (`Add ...`, `Fix ...`).

Al contribuir, aceptas que tu código se publique bajo la [licencia MIT](LICENSE).
