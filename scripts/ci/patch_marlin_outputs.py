#!/usr/bin/env python3
"""Post-process CreateConfigs output for Mriscoc New-Year-2025 compatibility."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Special_Configurations main still emits legacy DEFAULT_BED_KP names; New-Year-2025
# Marlin settings.cpp expects DEFAULT_bedKp / DEFAULT_Kp style symbols.
LEGACY_PID_RENAMES = (
    ("DEFAULT_BED_KP", "DEFAULT_bedKp"),
    ("DEFAULT_BED_KI", "DEFAULT_bedKi"),
    ("DEFAULT_BED_KD", "DEFAULT_bedKd"),
    ("DEFAULT_KP", "DEFAULT_Kp"),
    ("DEFAULT_KI", "DEFAULT_Ki"),
    ("DEFAULT_KD", "DEFAULT_Kd"),
)


def rename_legacy_pid_defines(text: str) -> str:
    for old, new in LEGACY_PID_RENAMES:
        text = re.sub(
            rf"(^\s*#define\s+){re.escape(old)}(\b.*)$",
            rf"\1{new}\2",
            text,
            flags=re.MULTILINE,
        )
    return text


def patch_version_h(path: Path, config_name: str) -> None:
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"^(\s*#define MACHINE_NAME\s+).*$",
        r'\1"Duender MGN9H beta"  // LCD boot name — beta channel',
        text,
        count=1,
        flags=re.MULTILINE,
    )

    text = re.sub(
        rf'(SHORT_BUILD_VERSION " ){re.escape(config_name)}, based on bugfix-2\.1\.x(")',
        r"\1Duender-422-BLTUBL-MPC-T13-beta.1 CoreXY, New-Year-2025\2",
        text,
        count=1,
    )

    path.write_text(text, encoding="utf-8")


def patch_configuration_h(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = rename_legacy_pid_defines(text)

    text = re.sub(
        r"^\s*#define\s+DISABLE_INACTIVE_EXTRUDER\b.*$",
        "#define DISABLE_OTHER_EXTRUDERS   // Keep only the active extruder enabled",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+([A-Z0-9_]+)_ENDSTOP_INVERTING\s+false\b.*$",
        r"#define \1_ENDSTOP_HIT_STATE HIGH",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+([A-Z0-9_]+)_ENDSTOP_INVERTING\s+true\b.*$",
        r"#define \1_ENDSTOP_HIT_STATE LOW",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+USE_[A-Z0-9_]+_PLUG\b.*$",
        lambda m: "//" + m.group(0).lstrip(),
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+Z_PROBE_OFFSET_RANGE_MIN\b",
        "#define PROBE_OFFSET_ZMIN",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+Z_PROBE_OFFSET_RANGE_MAX\b",
        "#define PROBE_OFFSET_ZMAX",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"^\s*#define\s+ProUIex\b", "#define PROUI_EX", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*#define\s+HAS_CGCODE\b.*$", "//#define HAS_CGCODE 1", text, flags=re.MULTILINE)

    if "SPEED_EDIT_MIN" not in text:
        text = text.replace(
            "#define HAS_LOCKSCREEN 1",
            "#define HAS_LOCKSCREEN 1\n#define SPEED_EDIT_MIN 10\n#define SPEED_EDIT_MAX 999\n"
            "#define FLOW_EDIT_MIN 10\n#define FLOW_EDIT_MAX 999",
            1,
        )

    if "DWIN_LCD_PROUI" in text:
        text = re.sub(
            r"^\s*#define\s+EXTENSIBLE_UI\b.*$",
            "//#define EXTENSIBLE_UI",
            text,
            flags=re.MULTILINE,
        )

    if not re.search(r"^\s*#define\s+EDITABLE_STEPS_PER_UNIT\b", text, flags=re.MULTILINE):
        text = re.sub(
            r"(^\s*#define\s+DEFAULT_MAX_FEEDRATE\b[^\n]*$)",
            "#define EDITABLE_STEPS_PER_UNIT\n\n\\1",
            text,
            count=1,
            flags=re.MULTILINE,
        )

    if "Z_MIN_PROBE_ENDSTOP_HIT_STATE" not in text:
        text = text.replace(
            "#define BLTOUCH  // 3D/CR/BLTouch version",
            "#define BLTOUCH  // 3D/CR/BLTouch version\n"
            "#define Z_MIN_PROBE_ENDSTOP_HIT_STATE HIGH  // 3D/CR/BLTouch version",
            1,
        )

    path.write_text(text, encoding="utf-8")


def patch_configuration_adv_h(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    text = re.sub(r"^\s*#define\s+AUTOTEMP\b.*$", "//#define AUTOTEMP", text, flags=re.MULTILINE)
    text = re.sub(r"LCD_SET_PROGRESS_MANUALLY", "SET_PROGRESS_MANUALLY", text)
    if "SET_PROGRESS_PERCENT" not in text:
        text = re.sub(
            r"^( *\#define\s+SET_PROGRESS_MANUALLY\b[^\n]*)$",
            r"\1\n"
            r"#if ENABLED(SET_PROGRESS_MANUALLY)\n"
            r"  #define SET_PROGRESS_PERCENT  // MRiscoC Allows display feedback of host printing through GCode M73\n"
            r"  #define SET_REMAINING_TIME    // MRiscoC Allows display feedback of host printing through GCode M73\n"
            r"#endif",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    text = re.sub(
        r"^\s*#define\s+INVERT_[A-Z0-9]+_STEP_PIN\b.*$",
        lambda m: "//" + m.group(0).lstrip(),
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+DISABLE_INACTIVE_EXTRUDER\b.*$",
        "#define DISABLE_OTHER_EXTRUDERS",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+DISABLE_INACTIVE_([XYZIJKUVWE])\b",
        r"#define DISABLE_IDLE_\1",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*#define\s+DEFAULT_STEPPER_DEACTIVE_TIME\b",
        "#define DEFAULT_STEPPER_TIMEOUT_SEC",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"^\s*#define\s+FOLDER_SORTING\b", "#define SDSORT_FOLDERS", text, flags=re.MULTILINE)
    text = re.sub(
        r"^\s*#define\s+BOOTSCREEN_TIMEOUT\s+\d+\b.*$",
        "#define BOOTSCREEN_TIMEOUT 1100       // (ms) Total Duration to display the boot screen(s)",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"\b([A-Z0-9]+)_MAX_CURRENT\b", r"\1_CURRENT", text)
    text = re.sub(r"\b([A-Z0-9]+)_SENSE_RESISTOR\b", r"\1_RSENSE", text)
    text = re.sub(
        r"(^\s*#define\s+[A-Z0-9]+_RSENSE\s+)91(\b.*$)",
        r"\g<1>0.091\2",
        text,
        flags=re.MULTILINE,
    )

    if "STEP_STATE_X" not in text:
        text = text.replace(
            "//#define INVERT_E_STEP_PIN false",
            "//#define INVERT_E_STEP_PIN false\n#define STEP_STATE_X HIGH\n#define STEP_STATE_Y HIGH\n"
            "#define STEP_STATE_Z HIGH\n#define STEP_STATE_I HIGH\n#define STEP_STATE_J HIGH\n"
            "#define STEP_STATE_K HIGH\n#define STEP_STATE_U HIGH\n#define STEP_STATE_V HIGH\n"
            "#define STEP_STATE_W HIGH\n#define STEP_STATE_E HIGH",
            1,
        )

    if "MULTISTEPPING_LIMIT" not in text:
        text = text.replace(
            "/**\n * Adaptive Step Smoothing increases the resolution of multi-axis moves, "
            "particularly at step frequencies",
            "#define MULTISTEPPING_LIMIT   16  //: [1, 2, 4, 8, 16, 32, 64, 128]\n\n"
            "/**\n * Adaptive Step Smoothing increases the resolution of multi-axis moves, "
            "particularly at step frequencies",
            1,
        )

    if not re.search(r"^\s*#define\s+CAPABILITIES_REPORT\b", text, flags=re.MULTILINE):
        text = re.sub(
            r"(^\s*#define\s+EXTENDED_CAPABILITIES_REPORT\s*$)",
            "#define CAPABILITIES_REPORT\n\\1",
            text,
            count=1,
            flags=re.MULTILINE,
        )

    if "DEBUG_FLAGS_GCODE" not in text:
        text = text.replace(
            "/**\n * Enable this option for a leaner build of Marlin that removes",
            "#define DEBUG_FLAGS_GCODE\n\n/**\n * Enable this option for a leaner build of Marlin that removes",
            1,
        )

    if "BLTOUCH_HS_MODE" in text and "BLTOUCH_HS_EXTRA_CLEARANCE" not in text:
        text = text.replace(
            "#define BLTOUCH_HS_MODE true",
            "#define BLTOUCH_HS_MODE true\n#define BLTOUCH_HS_EXTRA_CLEARANCE 0",
            1,
        )

    path.write_text(text, encoding="utf-8")


def patch_ui_api(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if "#if DISABLED(HAS_DWIN_E3V2)" in text and "#endif // !HAS_DWIN_E3V2" not in text:
        text = re.sub(
            r"(\n)(#endif\s*//\s*EXTENSIBLE_UI\s*)$",
            r"\1#endif // !HAS_DWIN_E3V2\2",
            text,
            count=1,
        )

    path.write_text(text, encoding="utf-8")


def patch_platformio_ini(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "default_envs = STM32F103RE_creality" not in text:
        text = text.replace(
            "default_envs = STM32F103RC_creality",
            "default_envs = STM32F103RE_creality",
        )
    path.write_text(text, encoding="utf-8")


def patch_stm32f1_ini(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    env_header = "[env:STM32F103RE_creality]"
    extui_filter = "build_src_filter = ${common_stm32.build_src_filter} -<src/lcd/extui>"

    if env_header not in lines:
        return

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


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} FIRMWARE_DIR CONFIG_NAME", file=sys.stderr)
        return 2

    firmware_dir = Path(sys.argv[1])
    config_name = sys.argv[2]

    steps = [
        ("Version.h", firmware_dir / "Marlin/Version.h", lambda p: patch_version_h(p, config_name)),
        ("Configuration.h", firmware_dir / "Marlin/Configuration.h", patch_configuration_h),
        ("Configuration_adv.h", firmware_dir / "Marlin/Configuration_adv.h", patch_configuration_adv_h),
        ("platformio.ini", firmware_dir / "platformio.ini", patch_platformio_ini),
        ("ui_api.cpp", firmware_dir / "Marlin/src/lcd/extui/ui_api.cpp", patch_ui_api),
        ("stm32f1.ini", firmware_dir / "ini/stm32f1.ini", patch_stm32f1_ini),
    ]
    optional = {"ui_api.cpp", "stm32f1.ini"}

    for label, path, fn in steps:
        if not path.is_file():
            if label in optional:
                continue
            print(f"patch failed ({label}): missing file: {path}", file=sys.stderr)
            return 1
        try:
            fn(path)
        except Exception as exc:  # noqa: BLE001 - surface patch failures in CI logs
            print(f"patch failed ({label}): {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
