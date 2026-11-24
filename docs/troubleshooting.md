# Troubleshooting

[Leer en español](es/troubleshooting.md)

Open the serial monitor to see what the ESP32 is doing:

```bash
cd firmware && pio device monitor
```

Every line starts with `[wifi]`, `[mqtt]`, `[dht]` or `[config]`. On the server side:

```bash
docker compose logs -f bridge mosquitto
```

---

## The ESP32 does not show up as a serial port / `pio run -t upload` fails

**Symptom:** `Could not open port`, `No such file or directory: '/dev/ttyUSB0'`, or the board does not appear in `pio device list`.

1. **Cable:** try another USB cable. Charge-only cables are the most common cause.
2. **Driver:** depending on your board's USB-serial chip (printed next to the connector):
   - CP2102/CP2104 → Silicon Labs *CP210x* driver.
   - CH340/CH9102 → WCH *CH34x* driver.
   - Recent macOS versions usually work with both without a driver; on Windows you normally have to install it.
3. **Permissions (Linux):** `sudo usermod -aG dialout $USER` and log in again.
4. **Port in use:** close the serial monitor (or another program such as the Arduino IDE) before uploading.
5. **Several ports:** pick the right one with `pio run -t upload --upload-port /dev/cu.usbserial-0001` (or `COM5` on Windows).

**Symptom:** `Failed to connect to ESP32: Timed out waiting for packet header`.

Hold the **BOOT** button when `Connecting....` appears and release it when writing starts. Some cheap boards do not enter flashing mode on their own.

---

## `[config] ... still has its example value`

**Symptom:** the serial monitor repeats every 5 s that `WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_USER` or `MQTT_PASSWORD` still has its example value, and the ESP32 does not try to connect.

Copy `firmware/include/config.example.h` to `firmware/include/config.h`, replace those four values (the MQTT user and password are the ones in `.env`) and flash again with `pio run -t upload`.

---

## Mosquitto or the bridge will not start: `still has its example value`

**Symptom:** `docker compose logs mosquitto bridge` shows `MQTT_PASSWORD still has its example value` or `These variables still have their example value: ...`, and the containers restart in a loop.

Mosquitto and the bridge refuse to start while any variable begins with `change-me`. Replace it in `.env` (for example with `openssl rand -hex 24`) and run `docker compose up -d`. On a fresh install, also change `INFLUX_ADMIN_PASSWORD` and `GRAFANA_ADMIN_PASSWORD`.

---

## `docker compose up` says `... is missing - copy .env.example to .env`

**Symptom:** `required variable MQTT_USER is missing a value`.

The `.env` file is missing from the repo root, or a variable is empty. Run `cp .env.example .env` and replace every value.

---

## The bridge exits with `Missing required environment variables`

**Symptom:** `docker compose logs bridge` lists the missing variables and the container restarts in a loop.

Create `.env` with `cp .env.example .env` and fill in every value, then `docker compose up -d`. If you run the bridge outside Docker, also export `MQTT_HOST` and `INFLUX_URL`.

---

## WiFi does not connect: `[wifi] failed, retry in ... ms`

- **5 GHz network:** the ESP32 only supports **2.4 GHz**. If your router uses a single name for both bands (band steering), create a separate 2.4 GHz network or disable steering.
- **WPA3 only:** use WPA2/WPA3 mixed mode or WPA2.
- **SSID/password:** they are case-sensitive; check `WIFI_SSID` and `WIFI_PASSWORD` in `firmware/include/config.h`.
- **Weak signal:** move the board closer to the router to rule out range.

The firmware retries with exponential backoff (1 s, 2 s, 4 s … up to 60 s), so you do not need to restart the board when the router comes back.

---

## MQTT does not connect: `[mqtt] failed, state=N`

| `state` | Meaning | What to check |
|---|---|---|
| `-4` | Timeout | Slow broker or congested network. |
| `-2` | Could not open the TCP connection | `MQTT_HOST` and firewall (see below). |
| `4` | Wrong user or password | `MQTT_USER`/`MQTT_PASSWORD` in `config.h` must match `.env`. |
| `5` | Not authorized | Same as `4`; Mosquitto rejects clients without valid credentials. |

**`state=-2`, typical causes:**

- `MQTT_HOST` cannot be `localhost` or `127.0.0.1`: it is the **local network** IP of the machine running Docker (`ipconfig getifaddr en0` on macOS, `hostname -I` on Linux).
- The machine's firewall blocks port 1883 (on macOS, allow incoming connections for Docker).
- The ESP32 and the server are on different networks (guest network, IoT VLAN with client isolation).

**You changed the credentials in `.env`:** Mosquitto's password file is regenerated on every start, so `docker compose up -d` is enough (it recreates the containers with the new variables). To check the credentials without the ESP32:

```bash
docker compose exec mosquitto mosquitto_pub -u <user> -P <password> -t devices/test/telemetry -m '{"temperature":20,"humidity":50}'
```

---

## NTP not synced (messages without `ts`)

**Symptom:** the serial monitor shows messages such as `{"temperature":22.50,"humidity":48.20}` without `ts`.

The firmware omits the timestamp until NTP syncs, and the bridge then uses the receive time. Data keeps arriving, with an error of a few milliseconds. If `ts` never appears:

- The network blocks UDP 123 to the internet (common on corporate or university networks).
- Set a local NTP server in `NTP_SERVER` (many routers offer one; try the router's IP).

---

## `[dht] read failed, check wiring`

- Check the wiring against [hardware.md](hardware.md); DATA must go to `GPIO4` (or to the `DHT_PIN` pin).
- The 10 kΩ pull-up resistor is missing (bare 4-pin sensor only).
- Cable too long at 3.3 V.
- Occasional failures are normal with the DHT22; the firmware discards that reading and tries again on the next cycle.

---

## No data in Grafana

1. **Do messages reach the broker?** Subscribe with `docker compose exec mosquitto mosquitto_sub -u <user> -P <password> -t 'devices/#' -v`.
2. **Does the bridge process them?** `docker compose logs bridge` should show one line per reading. `Dropped message ...` explains why one was discarded (invalid JSON, value outside the DHT22 range, wrong topic).
3. **Time range:** the dashboard shows the last 24 h; check the top-right corner.
4. **`Device` variable:** if you connected a new device, refresh the dashboard so it appears in the list.

---

## InfluxDB rejects the token after editing `.env`

InfluxDB only applies `INFLUX_ORG`, `INFLUX_BUCKET`, `INFLUX_TOKEN` and the admin user on the **first start** with an empty volume. If you change them later, the bridge and Grafana use values InfluxDB does not know (`unauthorized access` in the logs).

- If you do not care about the data: `docker compose down -v && docker compose up -d` (**deletes all** InfluxDB and Grafana data).
- If you want to keep it: put the original values back in `.env`.
