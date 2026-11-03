// Copy to config.h (git-ignored) and fill in your values.
#pragma once

#define WIFI_SSID          "your-wifi-ssid"
#define WIFI_PASSWORD      "your-wifi-password"

#define MQTT_HOST          "192.168.1.100"   // IP of the machine running docker compose
#define MQTT_PORT          1883
#define MQTT_USER          "your-mqtt-user"
#define MQTT_PASSWORD      "your-mqtt-password"

// Used as MQTT client id and in the topic devices/{DEVICE_ID}/telemetry
#define DEVICE_ID          "esp32-01"

#define DHT_PIN            4
#define READ_INTERVAL_MS   60000

// Calibration: added to every reading. Compare against a reference sensor.
#define TEMP_OFFSET_C      0.0f
#define HUMIDITY_OFFSET    0.0f

#define NTP_SERVER         "pool.ntp.org"
