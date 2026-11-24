#!/bin/sh
# Builds the password file from the environment on every start, then runs Mosquitto.
# Refuses to start with the example password so a copied .env.example is never exposed on the network.
set -eu

: "${MQTT_USER:?MQTT_USER is missing - copy .env.example to .env and fill it in}"
: "${MQTT_PASSWORD:?MQTT_PASSWORD is missing - copy .env.example to .env and fill it in}"

case "$MQTT_PASSWORD" in
  change-me*)
    echo "ERROR: MQTT_PASSWORD still has its example value ($MQTT_PASSWORD). Set a real one in .env, e.g. openssl rand -hex 24" >&2
    exit 1
    ;;
esac

mosquitto_passwd -c -b /mosquitto/data/passwd "$MQTT_USER" "$MQTT_PASSWORD"
chown mosquitto:mosquitto /mosquitto/data/passwd
chmod 0700 /mosquitto/data/passwd
exec mosquitto -c /mosquitto/config/mosquitto.conf
