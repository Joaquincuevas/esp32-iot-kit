# Hardware

[Leer en español](es/hardware.md)

## Components

| Component | Notes |
|---|---|
| ESP32 DevKit (ESP32-WROOM-32, 30 or 38 pins) | Any board compatible with the PlatformIO `esp32dev` target. |
| DHT22 (AM2302) sensor | 3-pin module (recommended, includes a pull-up resistor) or a bare 4-pin sensor. |
| 10 kΩ resistor | Only if you use the bare sensor. |
| Micro-USB / USB-C **data** cable | Many cables only charge and the board will not show up as a serial port. |
| 3 dupont wires | Female-to-female for the module; breadboard for the bare sensor. |

## Wiring

The firmware uses **GPIO4** for data (`DHT_PIN` in `config.h`).

### DHT22 module (3 pins)

| Module pin | ESP32 pin |
|---|---|
| `+` / VCC | `3V3` |
| `out` / DATA | `GPIO4` (labeled `D4` or `P4` on many boards) |
| `-` / GND | `GND` |

### Bare DHT22 sensor (4 pins, grille facing you, left to right)

| DHT22 pin | Connection |
|---|---|
| 1 VCC | `3V3` |
| 2 DATA | `GPIO4` + 10 kΩ resistor to `3V3` |
| 3 NC | not connected |
| 4 GND | `GND` |

```
ESP32 3V3 ──┬──────────── DHT22 pin 1 (VCC)
            │
          [10kΩ]
            │
ESP32 GPIO4 ┴──────────── DHT22 pin 2 (DATA)
ESP32 GND ─────────────── DHT22 pin 4 (GND)
```

## Power

- The ESP32 is powered over USB (5 V); its regulator provides 3.3 V on the `3V3` pin.
- The DHT22 works from 3.3 V to 6 V and draws ~1.5 mA while measuring. Power it from `3V3` so the DATA signal stays at 3.3 V, the ESP32's logic level. **Do not use 5 V with the DATA pin connected directly to the ESP32.**
- At 3.3 V keep the sensor cable short (< 1 m). For longer distances, use shielded cable or lower the pull-up resistor to 4.7 kΩ.
- For permanent use a 5 V / 1 A USB charger is enough. The board's average consumption with WiFi active is around 80–120 mA (deep sleep arrives in v0.2).

## If you change the pin

Use a bidirectional GPIO that is not a boot or flash pin:

- Avoid `GPIO6`–`GPIO11` (internal flash).
- Avoid `GPIO34`–`GPIO39` (input only; the DHT22 needs output).
- Avoid `GPIO0`, `GPIO2`, `GPIO5`, `GPIO12` and `GPIO15` (boot pins).

Good alternatives: `GPIO13`, `GPIO14`, `GPIO16`, `GPIO17`, `GPIO25`, `GPIO26`, `GPIO27`, `GPIO32`, `GPIO33`.

## Calibration

The DHT22 has a typical accuracy of ±0.5 °C and ±2–5 % RH, and each unit drifts a little differently. Compare it for a while against a reference thermo-hygrometer and adjust `TEMP_OFFSET_C` and `HUMIDITY_OFFSET` in `config.h`. The offset is added to every reading.

Place the sensor away from the ESP32 regulator and heat sources: the board warms up with WiFi active and can raise the measured temperature by 1–2 °C if they are touching.
