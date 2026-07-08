#!/usr/bin/env bash
# Generate Duender Marlin configs from mriscoc/Special_Configurations.
# Used locally and by .github/workflows/build-firmware.yml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FIRMWARE_DIR="${FIRMWARE_DIR:-$ROOT/upstream/Ender3V2S1}"
CONFIGS_DIR="${CONFIGS_DIR:-$ROOT/upstream/Special_Configurations}"
CONFIG_NAME="${CONFIG_NAME:-Duender-422-BLTUBL-MPC-T13}"
FEATURE_FILE="${FEATURE_FILE:-$ROOT/config/features/Duender-CoreXY-CI.json}"
PATCH_SCRIPT="$ROOT/scripts/ci/patch_marlin_outputs.py"
CREATE_SCRIPT="$ROOT/scripts/ci/run_create_configs.py"

if [[ ! -d "$FIRMWARE_DIR" ]]; then
  echo "Missing firmware tree: $FIRMWARE_DIR" >&2
  echo "Run: git submodule update --init --recursive" >&2
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

if [[ ! -f "$PATCH_SCRIPT" ]]; then
  echo "Missing patch script: $PATCH_SCRIPT" >&2
  exit 1
fi

if [[ ! -f "$CREATE_SCRIPT" ]]; then
  echo "Missing CreateConfigs runner: $CREATE_SCRIPT" >&2
  exit 1
fi

cp "$FEATURE_FILE" "$CONFIGS_DIR/_features/Duender-CoreXY.json"

if ! python3 "$CREATE_SCRIPT" "$CONFIGS_DIR" "$CONFIG_NAME"; then
  exit 1
fi

OUTPUT_DIR="$CONFIGS_DIR/$CONFIG_NAME"
for f in Configuration.h Configuration_adv.h Version.h platformio.ini; do
  if [[ ! -f "$OUTPUT_DIR/$f" ]]; then
    echo "Missing generated file: $OUTPUT_DIR/$f" >&2
    exit 1
  fi
done

if grep -q '___MEASURE___' "$OUTPUT_DIR/Configuration.h"; then
  echo "Unresolved ___MEASURE___ placeholders in Configuration.h" >&2
  echo "Use Duender-CoreXY-CI.json or fill values in Duender-CoreXY.json" >&2
  exit 1
fi

cp "$OUTPUT_DIR/Configuration.h" "$FIRMWARE_DIR/Marlin/"
cp "$OUTPUT_DIR/Configuration_adv.h" "$FIRMWARE_DIR/Marlin/"
cp "$OUTPUT_DIR/Version.h" "$FIRMWARE_DIR/Marlin/"
cp "$OUTPUT_DIR/platformio.ini" "$FIRMWARE_DIR/"

# Marlin 2.1.3+ preflight expects ANY/ALL instead of EITHER/BOTH in config headers.
for f in Configuration.h Configuration_adv.h; do
  if [[ -f "$FIRMWARE_DIR/Marlin/$f" ]]; then
    sed -i 's/BOTH(/ALL(/g; s/EITHER(/ANY(/g' "$FIRMWARE_DIR/Marlin/$f"
  fi
done

if ! python3 "$PATCH_SCRIPT" "$FIRMWARE_DIR" "$CONFIG_NAME"; then
  echo "Marlin output patch failed — see messages above" >&2
  exit 1
fi

echo "Applied $CONFIG_NAME to $FIRMWARE_DIR"
