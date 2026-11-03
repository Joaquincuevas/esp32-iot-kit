# Hardware

## Componentes

| Componente | Notas |
|---|---|
| ESP32 DevKit (ESP32-WROOM-32, 30 o 38 pines) | Cualquier placa compatible con el target `esp32dev` de PlatformIO. |
| Sensor DHT22 (AM2302) | Módulo de 3 pines (recomendado, trae resistencia pull-up) o sensor suelto de 4 pines. |
| Resistencia 10 kΩ | Solo si usas el sensor suelto. |
| Cable micro-USB / USB-C **de datos** | Muchos cables solo cargan y la placa no aparece como puerto serie. |
| 3 cables dupont | Hembra-hembra para módulo; protoboard para sensor suelto. |

## Cableado

El firmware usa **GPIO4** para datos (`DHT_PIN` en `config.h`).

### Módulo DHT22 (3 pines)

| Pin del módulo | Pin del ESP32 |
|---|---|
| `+` / VCC | `3V3` |
| `out` / DATA | `GPIO4` (rotulado `D4` o `P4` en muchas placas) |
| `-` / GND | `GND` |

### Sensor DHT22 suelto (4 pines, rejilla hacia ti, de izquierda a derecha)

| Pin DHT22 | Conexión |
|---|---|
| 1 VCC | `3V3` |
| 2 DATA | `GPIO4` + resistencia 10 kΩ hacia `3V3` |
| 3 NC | sin conexión |
| 4 GND | `GND` |

```
ESP32 3V3 ──┬──────────── DHT22 pin 1 (VCC)
            │
          [10kΩ]
            │
ESP32 GPIO4 ┴──────────── DHT22 pin 2 (DATA)
ESP32 GND ─────────────── DHT22 pin 4 (GND)
```

## Alimentación

- El ESP32 se alimenta por USB (5 V); su regulador entrega 3,3 V en el pin `3V3`.
- El DHT22 funciona entre 3,3 V y 6 V y consume ~1,5 mA midiendo. Aliméntalo desde `3V3` para que la señal DATA quede a 3,3 V, que es el nivel lógico del ESP32. **No uses 5 V con el pin DATA conectado directo al ESP32.**
- A 3,3 V mantén el cable del sensor corto (< 1 m). Para distancias mayores, usa cable apantallado o baja la resistencia pull-up a 4,7 kΩ.
- Para uso permanente basta un cargador USB de 5 V / 1 A. El consumo medio de la placa con WiFi activo ronda los 80–120 mA (el modo deep sleep llega en v0.2).

## Si cambias de pin

Usa un GPIO bidireccional que no sea de arranque ni de flash:

- Evita `GPIO6`–`GPIO11` (flash interna).
- Evita `GPIO34`–`GPIO39` (solo entrada; el DHT22 necesita salida).
- Evita `GPIO0`, `GPIO2`, `GPIO5`, `GPIO12` y `GPIO15` (pines de arranque).

Buenas alternativas: `GPIO13`, `GPIO14`, `GPIO16`, `GPIO17`, `GPIO25`, `GPIO26`, `GPIO27`, `GPIO32`, `GPIO33`.

## Calibración

El DHT22 tiene una precisión típica de ±0,5 °C y ±2–5 % HR, y cada unidad se desvía un poco distinto. Compáralo durante un rato con un termohigrómetro de referencia y ajusta `TEMP_OFFSET_C` y `HUMIDITY_OFFSET` en `config.h`. El offset se suma a cada lectura.

Coloca el sensor lejos del regulador del ESP32 y de fuentes de calor: la placa se calienta con el WiFi activo y puede subir la temperatura medida en 1–2 °C si están pegados.
