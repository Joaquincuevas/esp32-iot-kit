# Contributing

[Leer en español](docs/es/CONTRIBUTING.md)

Thanks for your interest. This template prioritizes being **clear and easy to use**: a change that makes it harder to understand needs a very good reason.

## Before you start

- For bugs, open an issue with: board, repo version, serial log (`pio device monitor`) and/or `docker compose logs bridge`. **Remove passwords and tokens** before pasting logs.
- For new features, open an issue first to discuss it; check the [Roadmap](README.md#roadmap).

## Development environment

```bash
# Firmware: must build without config.h (it falls back to config.example.h)
cd firmware && pio run

# Bridge: tests with Python 3.12
cd bridge && pip install -r requirements.txt pytest && pytest -q
# or without a local Python 3.12:
docker run --rm -v "$PWD/bridge:/app" -w /app python:3.12 sh -c "pip install -r requirements.txt pytest && pytest -q"

# Full stack
cp .env.example .env && docker compose config -q   # validates without starting anything
sh infra/mosquitto/test_entrypoint.sh
docker compose up -d
```

## Pull requests

1. Create a branch from `main`.
2. Keep the PR focused on a single change.
3. If you change the MQTT message format, update `parse_message` in the bridge, its tests and the README.
4. If you change configuration, update `config.example.h` or `.env.example` and the README table.
5. Add an entry under `Unreleased` in [CHANGELOG.md](CHANGELOG.md).
6. CI (`pio run`, `pytest`, `docker compose config` and the Mosquitto shell test) must pass.

## Style

- **Firmware:** Arduino-framework C++, no new dependencies if a few lines will do. Comment the *why*, not the *what*.
- **Bridge:** Python 3.12, standard library plus `paho-mqtt` and `influxdb-client` only. Configuration through environment variables only.
- **Secrets:** never in code or commits. Use placeholders in `*.example` files.
- **Commits:** in English and imperative mood (`Add ...`, `Fix ...`).

By contributing, you agree that your code is published under the [MIT license](LICENSE).
