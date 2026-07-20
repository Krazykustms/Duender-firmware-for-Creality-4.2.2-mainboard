# Hardware switch — Duender wiring → Klipper STM32 4.2.2

Power everything OFF first.

## Move these connectors off the Marlin GD32 board onto the Klipper STM32 board

Same Creality 4.2.2 layout — plugs match labels:

1. X motor (CoreXY A) → X  
2. Y motor (CoreXY B) → Y  
   (If X is pure but Y homes away from a **front** switch, invert `stepper_y` `dir_pin` and keep `position_endstop: 0` — do **not** move the endstop.)
3. Z motors (parallel) → Z
4. Sprite E motor → E
5. X / Y endstops
6. CR Touch → BLTouch header (signal / 5V / GND / servo)
7. Hotend heater + TH0 thermistor
8. Bed heater + TB thermistor
9. Part fan (FAN) / hotend fan as before
10. USB → BTT Pi (same CH340 cable)

Do NOT mix the GD32 Marlin board back in — leave it powered off / unplugged.

## After power-on

1. Confirm temps ~room temp in Mainsail / KlipperScreen
2. Firmware Restart if needed
3. TEST Z direction with motors free or Z clear — Marlin had Z sign quirks
4. Home X/Y only first (careful)
5. Probe Z home after CR Touch works
6. Recalibrate z_offset; optional PA / input shaper later

## Rollback

Keep the GD32 board + Marlin SD (`D-*.bin` in dist/) to swap back if needed.
