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
cp "$CONFIGS_DIR/$CONFIG_NAME/Version.h" "$FIRMWARE_DIR/Marlin/"
cp "$CONFIGS_DIR/$CONFIG_NAME/platformio.ini" "$FIRMWARE_DIR/"

# Marlin 2.1.3+ preflight expects ANY/ALL instead of EITHER/BOTH in config headers.
for f in Configuration.h Configuration_adv.h; do
  if [[ -f "$FIRMWARE_DIR/Marlin/$f" ]]; then
  sed -i 's/BOTH(/ALL(/g; s/EITHER(/ANY(/g' "$FIRMWARE_DIR/Marlin/$f"
  fi
done

# Compatibility cleanup for Special_Configurations output vs current Mriscoc New-Year-2025.
# Some generated config branches still emit old host progress and current symbols.
if [[ -f "$FIRMWARE_DIR/Marlin/Configuration.h" ]]; then
  python3 - "$FIRMWARE_DIR/Marlin/Configuration.h" <<'PY'
from pathlib import Path
import sys
import re

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

text = re.sub(
    r'^\s*#define\s+DISABLE_INACTIVE_EXTRUDER\b.*$',
    '#define DISABLE_OTHER_EXTRUDERS   // Keep only the active extruder enabled',
    text,
    count=1,
    flags=re.MULTILINE,
)
text = re.sub(
    r'^\s*#define\s+([A-Z0-9_]+)_ENDSTOP_INVERTING\s+false\b.*$',
    r'#define \1_ENDSTOP_HIT_STATE HIGH',
    text,
    flags=re.MULTILINE,
)
text = re.sub(
    r'^\s*#define\s+([A-Z0-9_]+)_ENDSTOP_INVERTING\s+true\b.*$',
    r'#define \1_ENDSTOP_HIT_STATE LOW',
    text,
    flags=re.MULTILINE,
)
text = re.sub(
    r'^\s*#define\s+USE_[A-Z0-9_]+_PLUG\b.*$',
    lambda m: '//' + m.group(0).lstrip(),
    text,
    flags=re.MULTILINE,
)
text = re.sub(r'^\s*#define\s+Z_PROBE_OFFSET_RANGE_MIN\b', '#define PROBE_OFFSET_ZMIN', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+Z_PROBE_OFFSET_RANGE_MAX\b', '#define PROBE_OFFSET_ZMAX', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+ProUIex\b', '#define PROUI_EX', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+HAS_CGCODE\b.*$', '//#define HAS_CGCODE 1', text, flags=re.MULTILINE)

if 'SPEED_EDIT_MIN' not in text:
    text = text.replace(
        '#define HAS_LOCKSCREEN 1',
        '#define HAS_LOCKSCREEN 1\n#define SPEED_EDIT_MIN 10\n#define SPEED_EDIT_MAX 999\n#define FLOW_EDIT_MIN 10\n#define FLOW_EDIT_MAX 999',
        1
    )

if 'DWIN_LCD_PROUI' in text:
    text = re.sub(r'^\s*#define\s+EXTENSIBLE_UI\b.*$', '//#define EXTENSIBLE_UI', text, flags=re.MULTILINE)

if not re.search(r'^\s*#define\s+EDITABLE_STEPS_PER_UNIT\b', text, flags=re.MULTILINE):
    text = re.sub(
        r'(^\s*#define\s+DEFAULT_MAX_FEEDRATE\b[^\n]*$)',
        '#define EDITABLE_STEPS_PER_UNIT\n\n\\1',
        text,
        count=1,
        flags=re.MULTILINE,
    )

if 'Z_MIN_PROBE_ENDSTOP_HIT_STATE' not in text:
    text = text.replace(
        '#define BLTOUCH  // 3D/CR/BLTouch version',
        '#define BLTOUCH  // 3D/CR/BLTouch version\n#define Z_MIN_PROBE_ENDSTOP_HIT_STATE HIGH  // 3D/CR/BLTouch version',
        1
    )

path.write_text(text, encoding="utf-8")
PY
fi

if [[ -f "$FIRMWARE_DIR/Marlin/Configuration_adv.h" ]]; then
  python3 - "$FIRMWARE_DIR/Marlin/Configuration_adv.h" <<'PY'
from pathlib import Path
import sys
import re

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

text = re.sub(r'^\s*#define\s+AUTOTEMP\b.*$', '//#define AUTOTEMP', text, flags=re.MULTILINE)
text = re.sub(r'LCD_SET_PROGRESS_MANUALLY', 'SET_PROGRESS_MANUALLY', text)
text = re.sub(r'^\s*#define\s+SET_PROGRESS_MANUALLY\b.*$', '//#define SET_PROGRESS_MANUALLY', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+INVERT_[A-Z0-9]+_STEP_PIN\b.*$', lambda m: '//' + m.group(0).lstrip(), text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+DISABLE_INACTIVE_EXTRUDER\b.*$', '#define DISABLE_OTHER_EXTRUDERS', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+DISABLE_INACTIVE_([XYZIJKUVWE])\b', r'#define DISABLE_IDLE_\1', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+DEFAULT_STEPPER_DEACTIVE_TIME\b', '#define DEFAULT_STEPPER_TIMEOUT_SEC', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+FOLDER_SORTING\b', '#define SDSORT_FOLDERS', text, flags=re.MULTILINE)
text = re.sub(r'^\s*#define\s+BOOTSCREEN_TIMEOUT\s+\d+\b.*$', '#define BOOTSCREEN_TIMEOUT 1100       // (ms) Total Duration to display the boot screen(s)', text, flags=re.MULTILINE)
text = re.sub(r'\b([A-Z0-9]+)_MAX_CURRENT\b', r'\1_CURRENT', text)
text = re.sub(r'\b([A-Z0-9]+)_SENSE_RESISTOR\b', r'\1_RSENSE', text)
text = re.sub(r'(^\s*#define\s+[A-Z0-9]+_RSENSE\s+)91(\b.*$)', r'\g<1>0.091\2', text, flags=re.MULTILINE)

if 'STEP_STATE_X' not in text:
    text = text.replace(
        '//#define INVERT_E_STEP_PIN false',
        '//#define INVERT_E_STEP_PIN false\n#define STEP_STATE_X HIGH\n#define STEP_STATE_Y HIGH\n#define STEP_STATE_Z HIGH\n#define STEP_STATE_I HIGH\n#define STEP_STATE_J HIGH\n#define STEP_STATE_K HIGH\n#define STEP_STATE_U HIGH\n#define STEP_STATE_V HIGH\n#define STEP_STATE_W HIGH\n#define STEP_STATE_E HIGH',
        1
    )

if 'MULTISTEPPING_LIMIT' not in text:
    text = text.replace(
        '/**\n * Adaptive Step Smoothing increases the resolution of multi-axis moves, particularly at step frequencies',
        '#define MULTISTEPPING_LIMIT   16  //: [1, 2, 4, 8, 16, 32, 64, 128]\n\n/**\n * Adaptive Step Smoothing increases the resolution of multi-axis moves, particularly at step frequencies',
        1
    )

if not re.search(r'^\s*#define\s+CAPABILITIES_REPORT\b', text, flags=re.MULTILINE):
    text = re.sub(
        r'(^\s*#define\s+EXTENDED_CAPABILITIES_REPORT\s*$)',
        '#define CAPABILITIES_REPORT\n\\1',
        text,
        count=1,
        flags=re.MULTILINE,
    )

if 'DEBUG_FLAGS_GCODE' not in text:
    text = text.replace(
        '/**\n * Enable this option for a leaner build of Marlin that removes',
        '#define DEBUG_FLAGS_GCODE\n\n/**\n * Enable this option for a leaner build of Marlin that removes',
        1
    )

if 'BLTOUCH_HS_MODE' in text and 'BLTOUCH_HS_EXTRA_CLEARANCE' not in text:
    text = text.replace(
        '#define BLTOUCH_HS_MODE true',
        '#define BLTOUCH_HS_MODE true\n#define BLTOUCH_HS_EXTRA_CLEARANCE 0',
        1
    )

path.write_text(text, encoding="utf-8")
PY
fi

# Mriscoc New-Year-2025: ui_api.cpp is missing #endif for #if DISABLED(HAS_DWIN_E3V2).
UI_API="$FIRMWARE_DIR/Marlin/src/lcd/extui/ui_api.cpp"
if [[ -f "$UI_API" ]]; then
  python3 - "$UI_API" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

if "#if DISABLED(HAS_DWIN_E3V2)" in text and "#endif // !HAS_DWIN_E3V2" not in text:
    text = re.sub(
        r"(\n)(#endif\s*//\s*EXTENSIBLE_UI\s*)$",
        r"\1#endif // !HAS_DWIN_E3V2\2",
        text,
        count=1,
    )

path.write_text(text, encoding="utf-8")
PY
fi

# Exclude extui when ProUI is active; env lives in ini/stm32f1.ini, not root platformio.ini.
STM32F1_INI="$FIRMWARE_DIR/ini/stm32f1.ini"
if [[ -f "$STM32F1_INI" ]]; then
  python3 - "$STM32F1_INI" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

env_header = "[env:STM32F103RE_creality]"
extui_filter = "build_src_filter = ${common_stm32.build_src_filter} -<src/lcd/extui>"
if env_header in lines:
    start = lines.index(env_header)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("["):
            end = i
            break
    block = lines[start:end]
    if not any("extui" in line for line in block if line.strip().startswith("build_src_filter")):
        lines.insert(end, extui_filter)

path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
fi

echo "Applied $CONFIG_NAME to $FIRMWARE_DIR"
