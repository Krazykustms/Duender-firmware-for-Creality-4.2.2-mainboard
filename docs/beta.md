# Beta firmware — Duender CoreXY on Creality 4.2.2

**Channel:** beta  
**Version:** `0.1.0-beta.1` (see [config/firmware-version.json](../config/firmware-version.json))  
**Profile:** `Duender-422-BLTUBL-MPC-T13` + `Duender-CoreXY` overlay

This is the first **config-complete, locally validated** build for Duender PIN v6 MGN9H using the Ender-3 V2 Neo donor stack (4.2.2 board, CR Touch, Sprite, DWIN ProUI).

## What “beta” means here

- Config generation and PlatformIO compile succeed against current Mriscoc upstream (`New-Year-2025` + `Special_Configurations` `main`).
- CoreXY, UBL, MPC, BLT, and T13 thermistor are enabled in the overlay.
- Bed/travel/probe numbers are **placeholders** from `Duender-CoreXY-CI.json` until you measure your frame.
- Treat as **experimental** until you homing-test, set motor directions, and run MPC/UBL calibration on your machine.

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

1. Rename `.bin` to a **unique** name (e.g. `Duender-beta-20260706.bin`).
2. FAT32 microSD, ≤32 GB, good card.
3. SD root → power cycle → wait for reboot (~30 s).

If the display stays blank, install the matching DWIN set from the [Mriscoc wiki](https://github.com/mriscoc/Ender3V2S1/wiki) before re-flashing mainboard firmware.

## After flash (minimum)

1. Confirm travel limits are safe (placeholder 230×230 mm bed).
2. Home X/Y — fix `INVERT_X_DIR` / `INVERT_Y_DIR` if needed.
3. MPC autotune hotend (`M306 T`), save (`M500`).
4. CR Touch Z offset + UBL mesh.

## Promote to stable

Stable release criteria (future `0.1.0`):

- [ ] Measured values in `Duender-CoreXY.json` committed (no `___MEASURE___`)
- [ ] Hardware smoke-test on at least one Duender PIN v6 build
- [ ] GitHub Release with attached `.bin` and changelog
