#!/usr/bin/env python3
from pathlib import Path

p = Path("/home/biqu/printer_data/config/printer.cfg")
t = p.read_text()
# Handle both active and already-commented forms
replacements = [
    (
        "[mcu CB1]\nserial: /tmp/klipper_host_mcu\n",
        "# Host MCU unused (ADXL/Pi GPIO later). Was causing 50↔49 MHz clock errors.\n"
        "# [mcu CB1]\n"
        "# serial: /tmp/klipper_host_mcu\n",
    ),
]
done = False
for old, new in replacements:
    if old in t:
        t = t.replace(old, new, 1)
        done = True
        break
if not done:
    raise SystemExit("CB1 block not found")
p.write_text(t)
print("CB1 disabled")
