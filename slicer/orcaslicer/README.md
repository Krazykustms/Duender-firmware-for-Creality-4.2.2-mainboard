# OrcaSlicer — Duender MGN9H

Starting profiles for the validated Duender CoreXY (Creality 4.2.2). **Functional, not tuned.** Now targets **Klipper**.

## Geometry

| Setting | Value |
|---------|-------|
| Printable polygon | `1x23` → `200x23` → `200x234` → `1x234` |
| Height | 280 mm |
| Structure | CoreXY |
| G-code | **Klipper** (`START_PRINT` / `END_PRINT`) |
| Nozzle | 0.4 mm |

## What Orca import requires

From Orca `PresetBundle::import_json_presets`:

1. **`version`** must be a parseable SemVer (e.g. `"2.4.0.1"`). Missing/invalid → silent skip → “0 configs imported”.
2. Type key: **`printer_settings_id`** (machine), **`print_settings_id`** (process), or **`filament_settings_id`**.
3. If **`inherits`** is set, that parent preset must already be **loaded** in your Orca session (installed vendor/printer). Non-empty inherit that cannot be found → skip.
4. Process **`compatible_printers`** must list a printer that exists (or its parent) after machine import.
5. Overwriting an existing user preset shows a confirm; answering No counts as not imported.

These profiles inherit **`MyMarlin 0.4 nozzle`** / **`0.20mm Standard @MyMarlin`** (present on this install) and override flavor + start/end for Klipper.

## Install

**Preferred (already done on this PC):** files live under  
`%APPDATA%\OrcaSlicer\user\<id>\machine\` and `\process\`. Restart Orca and pick **Duender MGN9H 0.4 nozzle**.

**Or File → Import → Import configs** (with Orca closed first if you replaced files manually):

1. Ensure **MyMarlin 0.4 nozzle** exists (Printer → Custom / Generic Marlin).
2. Import `machine/Duender MGN9H 0.4 nozzle.json`, then the process JSON.
3. If prompted to overwrite, choose Yes.
4. Confirm G-code flavor = Klipper and start/end call `START_PRINT` / `END_PRINT`.
