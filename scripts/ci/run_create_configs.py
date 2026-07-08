#!/usr/bin/env python3
"""Run mriscoc CreateConfigs with actionable CI logging."""

from __future__ import annotations

import os
import sys
from pathlib import Path

MODE = ["Ender3V2", "422", "BLT", "UBL", "MPC", "T13", "Duender-CoreXY"]


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} CONFIGS_DIR CONFIG_NAME", file=sys.stderr)
        return 2

    configs_dir = Path(sys.argv[1]).resolve()
    config_name = sys.argv[2]
    log_path = configs_dir / config_name / "log.txt"

    if not (configs_dir / "CreateConfigs.py").is_file():
        print(f"Missing CreateConfigs.py in {configs_dir}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(configs_dir))
    try:
        import CreateConfigs
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to import CreateConfigs: {exc}", file=sys.stderr)
        return 1

    os.chdir(configs_dir)
    try:
        error = CreateConfigs.Generate(config_name, MODE)
    except Exception as exc:  # noqa: BLE001
        print(f"CreateConfigs.Generate raised an exception: {exc}", file=sys.stderr)
        if log_path.is_file():
            print(log_path.read_text(encoding="utf-8"), file=sys.stderr)
        return 1

    if error:
        print(f"CreateConfigs reported errors for profile {config_name}", file=sys.stderr)
        if log_path.is_file():
            print(log_path.read_text(encoding="utf-8"), file=sys.stderr)
        else:
            print(f"Expected log file was not created: {log_path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
