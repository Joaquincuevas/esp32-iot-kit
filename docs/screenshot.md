# Captura del dashboard

El README muestra [`img/dashboard.svg`](img/dashboard.svg), que de momento es un **marcador**. Reemplázalo por una captura real siguiendo estos pasos.

## 1. Levanta el stack y genera datos de demostración

Con el stack corriendo (`docker compose up -d` desde la raíz del repo), publica 24 h de lecturas sintéticas para `demo-01`:

```bash
set -a; . ./.env; set +a
awk -v now="$(date +%s)" 'BEGIN { for (m = 1440; m >= 0; m -= 5) printf "{\"temperature\":%.2f,\"humidity\":%.2f,\"ts\":%d}\n", 21 + 3*sin(m/229), 50 + 8*cos(m/229), now - m*60 }' \
  | docker compose exec -T mosquitto mosquitto_pub -l -q 1 -u "$MQTT_USER" -P "$MQTT_PASSWORD" -t devices/demo-01/telemetry
```

También puedes dejar uno o dos ESP32 reales publicando unas horas: queda más natural.

## 2. Captura

1. Abre <http://localhost:3000/d/esp32-climate> e inicia sesión con `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD`.
2. Rango de tiempo: **Last 24 hours**. Tema: oscuro (el predeterminado).
3. Pulsa `v` sobre un panel o usa el modo kiosko (`?kiosk`) para ocultar menús: <http://localhost:3000/d/esp32-climate?kiosk&from=now-24h&to=now>
4. Ventana del navegador a **1600×900** aprox. y captura:
   - **PNG:** `Cmd+Shift+4` (macOS), `Win+Shift+S` (Windows).
   - **GIF** (opcional, p. ej. mostrando el selector de dispositivo): [Kap](https://getkap.co/) en macOS o [Peek](https://github.com/phw/peek) en Linux. Máximo ~5 MB y ~10 s.
5. Optimiza el archivo (`pngquant` o `gifsicle -O3`) y guárdalo como `docs/img/dashboard.png` (o `.gif`).

## 3. Actualiza el README

Cambia la ruta de la imagen en `README.md`, borra `docs/img/dashboard.svg` y haz commit.

## Limpiar los datos de demostración

```bash
docker compose exec influxdb influx delete --org "$INFLUX_ORG" --token "$INFLUX_TOKEN" --bucket "$INFLUX_BUCKET" \
  --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate 'device_id="demo-01"'
```
