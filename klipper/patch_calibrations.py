#!/usr/bin/env python3
"""Patch live printer.cfg: add PA + include calibrations.cfg; keep SAVE_CONFIG."""
from pathlib import Path

p = Path("/home/biqu/printer_data/config/printer.cfg")
t = p.read_text()

if "[include calibrations.cfg]" not in t:
    needle = "[include mainsail.cfg]\n"
    if needle not in t:
        raise SystemExit("mainsail include not found")
    t = t.replace(
        needle,
        needle + "[include calibrations.cfg]\n",
        1,
    )

pa_block = (
    "min_extrude_temp: 170\n"
    "pressure_advance: 0.0\n"
    "pressure_advance_smooth_time: 0.040\n"
)
if "pressure_advance:" not in t.split("SAVE_CONFIG")[0]:
    old = "min_extrude_temp: 170\n"
    if old not in t:
        raise SystemExit("min_extrude_temp not found")
    t = t.replace(old, pa_block, 1)

p.write_text(t)
print("printer.cfg patched OK")
