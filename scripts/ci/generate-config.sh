#!/usr/bin/env bash
# Generate Duender Marlin configs from mriscoc/Special_Configurations.
# Used locally and by .github/workflows/build-firmware.yml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FIRMWARE_DIR="${FIRMWARE_DIR:-$ROOT/upstream/Ender3V2S1}"
CONFIGS_DIR="${CONFIGS_DIR:-$ROOT/upstream/Special_Configurations}"
CONFIG_NAME="${CONFIG_NAME:-Duender-422-BLTUBL-MPC-T13}"
FEATURE_FILE="${FEATURE_FILE:-$ROOT/config/features/Duender-CoreXY-CI.json}"

if [[ ! -d "$FIRMWARE_DIR" ]]; then
  echo "Missing firmware tree: $FIRMWARE_DIR" >&2
  echo "Clone https://github.com/mriscoc/Ender3V2S1 into upstream/Ender3V2S1" >&2
  exit 1
fi

if [[ ! -d "$CONFIGS_DIR" ]]; then
  echo "Missing Special_Configurations: $CONFIGS_DIR" >&2
  exit 1
fi

if [[ ! -f "$FEATURE_FILE" ]]; then
  echo "Missing feature overlay: $FEATURE_FILE" >&2
  exit 1
fi

cp "$FEATURE_FILE" "$CONFIGS_DIR/_features/Duender-CoreXY.json"

(
  cd "$CONFIGS_DIR"
  python3 -c "import CreateConfigs; CreateConfigs.Generate('$CONFIG_NAME', ['Ender3V2','422','BLT','UBL','MPC','T13','Duender-CoreXY'])"
)

if grep -q '___MEASURE___' "$CONFIGS_DIR/$CONFIG_NAME/Configuration.h"; then
  echo "Unresolved ___MEASURE___ placeholders in Configuration.h" >&2
  echo "Use Duender-CoreXY-CI.json or fill values in Duender-CoreXY.json" >&2
  exit 1
fi

cp "$CONFIGS_DIR/$CONFIG_NAME/Configuration.h" "$FIRMWARE_DIR/Marlin/"
cp "$CONFIGS_DIR/$CONFIG_NAME/Configuration_adv.h" "$FIRMWARE_DIR/Marlin/"
cp "$CONFIGS_DIR/$CONFIG_NAME/platformio.ini" "$FIRMWARE_DIR/"

echo "Applied $CONFIG_NAME to $FIRMWARE_DIR"
