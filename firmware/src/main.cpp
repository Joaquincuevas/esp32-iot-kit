#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <time.h>

#ifdef USE_EXAMPLE_CONFIG
#warning "include/config.h not found: building with config.example.h placeholders"
#include "config.example.h"
#else
#include "config.h"
#endif

static const char TOPIC[] = "devices/" DEVICE_ID "/telemetry";
static const uint32_t WIFI_CONNECT_TIMEOUT_MS = 15000;
static const time_t MIN_VALID_EPOCH = 1700000000;  // anything earlier means NTP has not synced

// Exponential backoff between reconnect attempts: 1 s, 2 s, 4 s ... capped at 60 s.
struct Backoff {
  uint32_t waitMs = 0;
  uint32_t lastAttempt = 0;

  bool due() const { return millis() - lastAttempt >= waitMs; }
  void failed() {
    lastAttempt = millis();
    waitMs = waitMs ? min<uint32_t>(waitMs * 2, 60000) : 1000;
  }
  void reset() { waitMs = 0; }
};

DHT dht(DHT_PIN, DHT22);
WiFiClient net;
PubSubClient mqtt(net);
Backoff wifiBackoff, mqttBackoff;
uint32_t lastReadMs;
bool readPending = true;

bool ensureWifi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  if (!wifiBackoff.due()) return false;

  Serial.printf("[wifi] connecting to %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  if (WiFi.waitForConnectResult(WIFI_CONNECT_TIMEOUT_MS) == WL_CONNECTED) {
    Serial.printf("[wifi] connected, ip=%s\n", WiFi.localIP().toString().c_str());
    wifiBackoff.reset();
    return true;
  }
  WiFi.disconnect();
  wifiBackoff.failed();
  Serial.printf("[wifi] failed, retry in %u ms\n", wifiBackoff.waitMs);
  return false;
}

bool ensureMqtt() {
  if (mqtt.connected()) return true;
  if (!mqttBackoff.due()) return false;

  Serial.printf("[mqtt] connecting to %s:%d\n", MQTT_HOST, MQTT_PORT);
  if (mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD)) {
    Serial.println("[mqtt] connected");
    mqttBackoff.reset();
    return true;
  }
  mqttBackoff.failed();
  Serial.printf("[mqtt] failed, state=%d, retry in %u ms\n", mqtt.state(), mqttBackoff.waitMs);
  return false;
}

void publishReading() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) {
    Serial.println("[dht] read failed, check wiring");
    return;
  }

  char payload[96];
  time_t now = time(nullptr);
  // Without NTP the timestamp is omitted and the bridge uses its receive time.
  if (now >= MIN_VALID_EPOCH) {
    snprintf(payload, sizeof(payload), "{\"temperature\":%.2f,\"humidity\":%.2f,\"ts\":%ld}",
             t + TEMP_OFFSET_C, h + HUMIDITY_OFFSET, (long)now);
  } else {
    snprintf(payload, sizeof(payload), "{\"temperature\":%.2f,\"humidity\":%.2f}",
             t + TEMP_OFFSET_C, h + HUMIDITY_OFFSET);
  }

  bool ok = mqtt.publish(TOPIC, payload);
  Serial.printf("[mqtt] %s %s %s\n", ok ? "published" : "publish failed", TOPIC, payload);
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.mode(WIFI_STA);
  configTime(0, 0, NTP_SERVER);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (!ensureWifi() || !ensureMqtt()) return;
  mqtt.loop();

  if (readPending || millis() - lastReadMs >= READ_INTERVAL_MS) {
    readPending = false;
    lastReadMs = millis();
    publishReading();
  }
}
