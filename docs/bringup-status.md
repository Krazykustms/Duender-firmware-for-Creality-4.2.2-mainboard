# Bring-up status

Current machine state as of early hardware bring-up.

## Summary

The Duender conversion is not yet mechanically complete for CoreXY motion because the X/Y pulleys and belts have not arrived yet.

Even so, the reused **Ender-3 V2 Neo** electronics package has already been validated with stock **Mriscoc Professional** firmware in its original cartesian setup. This is the baseline before enabling `COREXY`.

## Confirmed working

- X endstop installed and tested
- Y endstop installed and tested
- Bed can be raised from the screen controls
- General motor control from the display is working
- Extruder motor tested
- Bed heater tested
- Manual electronic control is functioning with Mriscoc firmware
- Printer currently runs and responds correctly with cartesian `Ender3V2-422-BLTUBL-MPC`
- Z direction behavior is now known for the conversion: current cartesian-style direction makes `Z+` move the bed **up**, so final Duender firmware must flip `INVERT_Z_DIR` while keeping the existing Z wiring unchanged

## Not yet validated

- X/Y CoreXY belt path
- X/Y pulleys installed
- Belt tensioning
- CoreXY motor mixing
- Final `INVERT_X_DIR` / `INVERT_Y_DIR` values under CoreXY
- Final travel limits
- Final CR Touch probe offset on the Duender toolhead

## Why this matters

This is the safest order of operations for the conversion:

1. Prove the electronics with known-good cartesian firmware.
2. Finish the mechanical CoreXY belt system.
3. Switch to the Duender `COREXY` configuration.
4. Validate homing direction and small X/Y moves.
5. Measure final bed, travel, and probe values.

Passing cartesian tests means the board, display, heaters, motors, and endstops are healthy. It does **not** yet prove that CoreXY motion will be correct once the belts are installed.

One useful result has already come out of bring-up, though: the final machine should **not** keep the stock Z direction. On this conversion, `Z+` currently raises the bed instead of lowering it away from the nozzle.

## Next milestone

After the X/Y pulleys and belts are installed:

1. Flash the Duender `COREXY` build.
2. Test `G28 X` and `G28 Y` separately.
3. Verify `INVERT_Z_DIR` with a safe `Z+` jog before trusting probe motion.
4. Test small jogs like `G0 X10` and `G0 Y10`.
5. Correct motor direction if needed.
6. Measure `X_BED_SIZE`, `Y_BED_SIZE`, `X_MAX_POS`, `Y_MAX_POS`, `Z_MAX_POS`, and `NOZZLE_TO_PROBE_OFFSET`.

## Working assumption

Until CoreXY motion is physically complete, the cartesian Mriscoc baseline should be treated as the known-good recovery point.
