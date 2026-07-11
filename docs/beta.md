# Beta firmware — Duender CoreXY on Creality 4.2.2

**Channel:** beta  
**Version:** `0.1.0-beta.3` (see [config/firmware-version.json](../config/firmware-version.json))  
**Profile:** `Duender-422-BLTUBL-MPC-T13` + `Duender-CoreXY` overlay  
**Hardware status:** **fully functional, not tuned** — jog, home, dual tram, probe-reachable UBL, Orca profile validated on one machine

## What “beta” means here

- Config generation and PlatformIO compile succeed against current Mriscoc upstream (`New-Year-2025` + `Special_Configurations` `main`).
- CoreXY, UBL, MPC, BLT, and T13 thermistor are enabled in the overlay.
- Bed/travel/probe/tram numbers in `Duender-CoreXY-CI.json` / `Duender-CoreXY.json` are **measured on a Duender PIN v6 MGN9H**.
- Motion quality (IS, LA, accel) and slicer centering are **not** finished — safe for bring-up and first prints, not a polished release.

## Validated motion / geometry

| Item | Value |
|------|--------|
| Kinematics | `COREXY` |
| Motor plugs | Normal (X→X, Y→Y) — do not swap; do not flip one plug 180° |
| `INVERT_X_DIR` / `INVERT_Y_DIR` | both `true` |
| Y endstop | Front-left, `Y_HOME_DIR -1` |
| Steps/mm | X/Y 100, Z 400, E 424.9 |
| Probe XY | `{ -31, -39, 0 }` |
| Bed travel | 0,0 → 201,235 |
| Print area (nozzle) | 1,23 → 200,234 |
| UBL mesh (probe tip) | 10,23 → 170,196 |
| Tram manual | FL(1,22) FR(201,22) BR(201,235) BL(1,235) |
| Tram auto/probe | FL(19,61) FR(170,61) BR(170,196) BL(19,196) |

Print area and UBL mesh are **different on purpose**: mesh must stay inside probe reach with offset `{ -31, -39 }`. Absolute tram points are applied from [`patches/bed_tramming.cpp`](../patches/bed_tramming.cpp) during config generation.

## Build target — GD32F303RET6 Neo (Creality 4.2.2)

This project targets **GigaDevice GD32F303RET6** on the Ender-3 V2 Neo **4.2.2** board (512 KB flash). Full reference: [board-mcu.md](board-mcu.md).

Mriscoc requires the **`STM32F103RE_creality`** PlatformIO environment for this hardware. That name is **not** the physical chip — it is the 512K Creality 4.2.2 profile.

| Physical MCU on your board | PlatformIO env | OK for this repo? |
|----------------------------|------------------|-------------------|
| **GD32F303RET6** (Neo 4.2.2) | `STM32F103RE_creality` | **Yes** |
| STM32F103RCT6 (256K 4.2.2 only) | `STM32F103RC_creality` | **No — wrong flash size** |

Do **not** use `GD32F303RE_creality_maple` — ProUI prebuild scripts do not support it on current Mriscoc builds.

## Get a beta binary

### CI artifact (recommended after merge)

[Actions workflow](../.github/workflows/build-firmware.yml) uploads `Duender-422-BLTUBL-MPC-T13-CoreXY-*.bin` artifacts.

### Build locally

See [build.md](build.md). Summary:

```bash
# Short paths on Windows (e.g. C:\fw\...)
git clone --recurse-submodules https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard.git
cd Duender-firmware-for-Creality-4.2.2-mainboard
git clone -b main https://github.com/mriscoc/Special_Configurations.git upstream/Special_Configurations
bash scripts/ci/generate-config.sh
cd upstream/Ender3V2S1   # or your FIRMWARE_DIR
pio run -e STM32F103RE_creality
```

The first `pio run` may stop once to rewrite `EITHER`/`BOTH` macros in config headers; run again if needed (or use the updated `generate-config.sh`, which applies that step automatically).

## Flash

1. Rename `.bin` to a **unique** name (e.g. `D-beta3.bin`).
2. FAT32 microSD, ≤32 GB, good card.
3. SD root → power cycle → wait for reboot (~30 s).

If the display stays blank, install the matching DWIN set from the [Mriscoc wiki](https://github.com/mriscoc/Ender3V2S1/wiki) before re-flashing mainboard firmware.

## After flash (minimum)

1. `M502` then `M500` (or LCD restore defaults + store).
2. Confirm Physical Settings match measured bed/print sizes.
3. Re-set CR Touch Z offset (`M851` / LCD) and `M500`.
4. Home X/Y/Z; run tram if needed; build UBL mesh; enable with `M420 S1`.

## Slicer

OrcaSlicer starting point: [`slicer/orcaslicer/`](../slicer/orcaslicer/) (Custom **Duender MGN9H** / Generic Marlin base). Host baud in firmware is **250000**.

## Not tuned yet

- Input Shaping / Linear Advance
- Aggressive CoreXY accel
- Perfect slicer centering on the physical bed
