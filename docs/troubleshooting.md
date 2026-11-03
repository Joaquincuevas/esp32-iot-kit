# Troubleshooting

Abre el monitor serie para ver qué está haciendo el ESP32:

```bash
cd firmware && pio device monitor
```

Cada línea empieza con `[wifi]`, `[mqtt]` o `[dht]`. Del lado del servidor:

```bash
docker compose logs -f bridge mosquitto
```

---

## El ESP32 no aparece como puerto serie / `pio run -t upload` falla

**Síntoma:** `Could not open port`, `No such file or directory: '/dev/ttyUSB0'` o la placa no aparece en `pio device list`.

1. **Cable:** prueba otro cable USB. Los cables que solo cargan son la causa más común.
2. **Driver:** según el chip USB-serie de tu placa (está impreso al lado del conector):
   - CP2102/CP2104 → driver *CP210x* de Silicon Labs.
   - CH340/CH9102 → driver *CH34x* de WCH.
   - En macOS recientes ambos suelen funcionar sin driver; en Windows normalmente hay que instalarlo.
3. **Permisos (Linux):** `sudo usermod -aG dialout $USER` y vuelve a iniciar sesión.
4. **Puerto ocupado:** cierra el monitor serie (u otro programa como Arduino IDE) antes de subir.
5. **Varios puertos:** fija el correcto con `pio run -t upload --upload-port /dev/cu.usbserial-0001` (o `COM5` en Windows).

**Síntoma:** `Failed to connect to ESP32: Timed out waiting for packet header`.

Mantén pulsado el botón **BOOT** cuando aparezca `Connecting....` y suéltalo cuando empiece a escribir. Algunas placas baratas no entran solas en modo de carga.

---

## WiFi no conecta: `[wifi] failed, retry in ... ms`

- **Red de 5 GHz:** el ESP32 solo soporta **2,4 GHz**. Si tu router usa un único nombre para ambas bandas (band steering), crea una red de 2,4 GHz separada o desactiva el steering.
- **WPA3 únicamente:** usa modo mixto WPA2/WPA3 o WPA2.
- **SSID/contraseña:** distinguen mayúsculas; revisa `WIFI_SSID` y `WIFI_PASSWORD` en `firmware/include/config.h`.
- **Señal débil:** acerca la placa al router para descartar alcance.

El firmware reintenta con backoff exponencial (1 s, 2 s, 4 s … máximo 60 s), así que no hace falta reiniciar la placa cuando el router vuelve.

---

## MQTT no conecta: `[mqtt] failed, state=N`

| `state` | Significado | Qué revisar |
|---|---|---|
| `-4` | Timeout | Broker lento o red saturada. |
| `-2` | No se pudo abrir la conexión TCP | `MQTT_HOST` y firewall (ver abajo). |
| `4` | Usuario o contraseña incorrectos | `MQTT_USER`/`MQTT_PASSWORD` en `config.h` deben coincidir con `.env`. |
| `5` | No autorizado | Igual que `4`; Mosquitto rechaza clientes sin credenciales válidas. |

**`state=-2`, causas típicas:**

- `MQTT_HOST` no puede ser `localhost` ni `127.0.0.1`: es la IP **en tu red local** del equipo que corre Docker (`ipconfig getifaddr en0` en macOS, `hostname -I` en Linux).
- El firewall del equipo bloquea el puerto 1883 (en macOS, permite conexiones entrantes a Docker).
- El ESP32 y el servidor están en redes distintas (red de invitados, VLAN de IoT con aislamiento de clientes).

**Cambiaste las credenciales en `.env`:** el archivo de contraseñas de Mosquitto se regenera en cada arranque, así que basta con `docker compose up -d` (recrea los contenedores con las variables nuevas). Para comprobar las credenciales sin el ESP32:

```bash
docker compose exec mosquitto mosquitto_pub -u <usuario> -P <contraseña> -t devices/test/telemetry -m '{"temperature":20,"humidity":50}'
```

---

## NTP sin sincronizar (mensajes sin `ts`)

**Síntoma:** el monitor serie muestra mensajes como `{"temperature":22.50,"humidity":48.20}` sin `ts`.

El firmware omite el timestamp hasta que NTP sincroniza, y el bridge usa entonces la hora de recepción. Los datos siguen llegando, con un error de pocos milisegundos. Si nunca aparece `ts`:

- La red bloquea UDP 123 hacia internet (común en redes corporativas o de universidad).
- Configura un servidor NTP local en `NTP_SERVER` (muchos routers lo ofrecen; prueba con la IP del router).

---

## `[dht] read failed, check wiring`

- Revisa el cableado con [hardware.md](hardware.md); DATA debe ir a `GPIO4` (o al pin de `DHT_PIN`).
- Falta la resistencia pull-up de 10 kΩ (solo en sensor suelto de 4 pines).
- Cable demasiado largo a 3,3 V.
- Fallos aislados son normales en el DHT22; el firmware descarta esa lectura y lo intenta en el siguiente ciclo.

---

## No hay datos en Grafana

1. **¿Llegan los mensajes al broker?** Suscríbete con `docker compose exec mosquitto mosquitto_sub -u <usuario> -P <contraseña> -t 'devices/#' -v`.
2. **¿Los procesa el bridge?** `docker compose logs bridge` debe mostrar una línea por lectura. `Dropped message ...` explica por qué se descartó (JSON inválido, valor fuera de rango del DHT22, topic incorrecto).
3. **Rango de tiempo:** el dashboard muestra las últimas 24 h; revisa la esquina superior derecha.
4. **Variable `Device`:** si conectaste un dispositivo nuevo, refresca el dashboard para que aparezca en la lista.

---

## InfluxDB rechaza el token después de editar `.env`

InfluxDB solo aplica `INFLUX_ORG`, `INFLUX_BUCKET`, `INFLUX_TOKEN` y el usuario admin en el **primer arranque** con el volumen vacío. Si los cambias después, el bridge y Grafana usan valores que InfluxDB no conoce (`unauthorized access` en los logs).

- Si no te importan los datos: `docker compose down -v && docker compose up -d` (**borra todos los datos** de InfluxDB y Grafana).
- Si quieres conservarlos: vuelve a poner en `.env` los valores originales.
