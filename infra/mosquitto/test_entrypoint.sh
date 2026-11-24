#!/bin/sh
# Run: sh infra/mosquitto/test_entrypoint.sh   (needs only POSIX sh; real Mosquitto tools are stubbed)
set -u
here=$(cd "$(dirname "$0")" && pwd)
stubs=$(mktemp -d)
trap 'rm -rf "$stubs"' EXIT
for tool in mosquitto_passwd chown chmod mosquitto; do
  printf '#!/bin/sh\necho "stub %s $*"\n' "$tool" > "$stubs/$tool"
  chmod +x "$stubs/$tool"
done
fail=0
check() { if [ "$2" != "$3" ]; then echo "FAIL: $1 (expected $2, got $3)"; fail=1; else echo "ok: $1"; fi; }

out=$(PATH="$stubs:$PATH" MQTT_USER=esp32 MQTT_PASSWORD=change-me-mqtt sh "$here/entrypoint.sh" 2>&1); rc=$?
check "rejects example password" 1 "$rc"
case "$out" in *"example value"*) check "explains why" 0 0;; *) check "explains why" 0 1;; esac
case "$out" in *"stub mosquitto"*) check "does not start broker" 0 1;; *) check "does not start broker" 0 0;; esac

out=$(PATH="$stubs:$PATH" MQTT_USER=esp32 sh "$here/entrypoint.sh" 2>&1); rc=$?
check "rejects missing password" 1 "$rc"

out=$(PATH="$stubs:$PATH" MQTT_USER=esp32 MQTT_PASSWORD=0123456789abcdef sh "$here/entrypoint.sh" 2>&1); rc=$?
check "accepts a real password" 0 "$rc"
case "$out" in *"stub mosquitto -c"*) check "starts broker" 0 0;; *) check "starts broker" 0 1;; esac

exit $fail
