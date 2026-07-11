# OrcaSlicer — Duender MGN9H

Starting profiles for the validated Duender CoreXY (Creality 4.2.2 / Mriscoc). **Functional, not tuned.**

## Geometry

| Setting | Value |
|---------|-------|
| Printable polygon | `1x23` → `200x23` → `200x234` → `1x234` |
| Height | 280 mm |
| Structure | CoreXY |
| G-code | Marlin 2 |
| Nozzle | 0.4 mm (Sprite) |
| Host baud | **250000** |

Firmware bed travel is larger (`0,0`–`201,235`). Slicer uses the **print** rectangle. UBL mesh in firmware is probe-limited (`~10–170` × `23–196`); start G-code uses `M420 S1`.

Prints may sit slightly off physical bed center (print origin inset) — acceptable until centering is tuned.

## Install

On the bring-up machine, **Custom → Generic Marlin** was renamed/overlaid to **Duender MGN9H** under Orca’s system Custom vendor. Repo JSON under `machine/` is the same geometry for import elsewhere:

1. Prefer: copy settings from an existing **MyMarlin / Generic Marlin** printer in Orca, or  
2. **File → Import → Import configs** and select the JSON files here.

## Not tuned

Accel/jerk, Input Shaping, Linear Advance, and dead-center placement are still open.
