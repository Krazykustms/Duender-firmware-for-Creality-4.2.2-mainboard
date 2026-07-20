# Happy Hare Custom — ACE Gen1 mechanics (Duender)

Companion to [ace-mechanics-mmu.md](ace-mechanics-mmu.md).

## Install (BTT Pi)

```bash
cd /home/biqu
git clone https://github.com/moggieuk/Happy-Hare.git
cd Happy-Hare
./install.sh
```

When prompted:

| Prompt | Answer for this project |
|--------|-------------------------|
| MMU type | **Custom** / Other (not BoxTurtle, not ERCF unless inventory matches) |
| Number of gates | **4** |
| MCU for gear | board named **`ace`** (`[mcu ace]` in `ace_mmu.cfg`) |
| Selector | Stepper **or** none + clutch pin — from inventory |
| Toolhead sensor | Yes — `toolhead_sensor` in `ace_toolhead.cfg` |
| Cutter | Toolhead servo cutter — map to `MMU_CUT_FILAMENT` / HH cutter macros |

Installer writes under `~/printer_data/config/mmu/`. Do **not** overwrite blindly with repo copies without merging pins.

## After install

1. Copy from this repo to Pi (if not already):

   - `ace_mmu.cfg`
   - `ace_toolhead.cfg`
   - `ace-mechanics-mmu.md`

2. In `printer.cfg` uncomment:

   ```ini
   [include ace_mmu.cfg]
   [include ace_toolhead.cfg]
   [include mmu/base/*.cfg]   # path Happy Hare created
   ```

3. Set `[mcu ace] serial:` to the GD32 (or extra MCU) by-id string.

4. Edit Happy Hare `mmu_hardware.cfg` / pin aliases so:

   - gear stepper = `mmu_gear` (or HH’s expected `manual_stepper` name — match installer)
   - gate sensors = `mmu_gate_0` … `mmu_gate_3`
   - toolhead sensor = `toolhead_sensor`
   - cutter calls `MMU_CUT_FILAMENT` or HH built-in cutter pin

5. `FIRMWARE_RESTART` — fix pin errors until clean.

## Bring-up sequence (before Orca)

```text
ACE_SENSOR_QUERY
ACE_GEAR_TEST DIST=5
CUTTER_TEST
MMU_HOME          # or Happy Hare equivalent
# Select gate 0, load to toolhead, unload, gate 1…
```

Only then configure Orca multi-tool (see `slicer/orcaslicer/ACE-MMU-NOTES.md`).

## Moonraker

Happy Hare’s installer usually adds an update-manager entry. Confirm in Mainsail → Machine → Update.

## Conceptual MMU type

ACE Gen1 ≈ **shared gear + selector/clutch** (Happy Hare Type-A / selector class), **not** Type-B independent lane steppers (BoxTurtle / ACE 2 Pro). Read: https://github.com/moggieuk/Happy-Hare/wiki/Conceptual-MMU
