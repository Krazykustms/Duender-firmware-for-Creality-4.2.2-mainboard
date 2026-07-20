# OrcaSlicer — Duender + Happy Hare ACE mechanics MMU

Use after Klipper can load/unload gates manually (see `klipper/ace_mmu_happy_hare.md`).

## Machine / extruder

- Printer: Duender MGN9H (Klipper / Moonraker).
- Extruders / tools: **4** (T0–T3) mapped 1:1 to ACE gates 0–3.
- Single physical nozzle (Sprite) — multi-tool is virtual for filament changes.

## Toolchange G-code

Prefer Happy Hare’s toolchange (installed macros vary by version). Typical:

```gcode
; Tool change — Happy Hare
T{next_extruder}
```

If your HH build expects explicit:

```gcode
MMU_CHANGE_TOOL TOOL={next_extruder}
```

Confirm which command exists in Mainsail console (`HELP` / HH docs) after install.

Park / tip / purge are usually handled by Happy Hare macros — do **not** duplicate long Marlin-style tip forming in Orca unless HH is in bypass mode.

## Start / end

Keep existing Duender START/END (heat, home, mesh) from the Duender Klipper profiles. Ensure START does **not** assume single filament only; HH often wants filament already loaded in the active gate or will load on first `T`.

## First calibration prints

1. **2-color** purge tower / color swap cube (low layer count).  
2. Tune purge volumes / tip in Happy Hare, not only Orca.  
3. Then **4-color** test.

Filament dryer can stay manual until a Klipper `[heater_generic]` is wired for the ACE heater.

## Host

- Host Type: Octo/Klipper or Moonraker  
- IP: `192.168.1.235` (BTT Pi) port `7125`
