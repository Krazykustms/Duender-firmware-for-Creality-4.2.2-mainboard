# Build and flash — Mriscoc Professional for Duender

**Beta:** `0.1.0-beta.3` — fully functional, not tuned — read [beta.md](beta.md) before flashing.

## Prerequisites

- [PlatformIO](https://platformio.org/) (VS Code extension or CLI)
- Python 3 (for `CreateConfigs.py` only)
- USB data cable — Creality 4.2.2 uses **USB-serial on USART1** via the display cable, or direct USB depending on your board revision

Keep clone paths **short** on Windows (e.g. `C:\fw\...`). PlatformIO fails on deep paths and long-path git checkouts.

## 1. Clone repo and upstream inputs

```bash
mkdir -p ~/duender-fw && cd ~/duender-fw   # or C:\fw on Windows

git clone --recurse-submodules https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard.git duender-config
git clone -b main https://github.com/mriscoc/Special_Configurations.git duender-config/upstream/Special_Configurations
```

If you already cloned this repo without submodules:

```bash
cd duender-config
git submodule update --init --recursive
```

Set paths if not using `upstream/` under the config repo:

```bash
export FIRMWARE_DIR="$PWD/duender-config/upstream/Ender3V2S1"
export CONFIGS_DIR="$PWD/duender-config/upstream/Special_Configurations"
```

## 2. Generate configuration

**Recommended — use the helper script:**

```bash
cd duender-config
bash scripts/ci/generate-config.sh
```

This copies `Duender-CoreXY-CI.json` by default (measured D025 geometry). For the same machine profile file:

```bash
export FEATURE_FILE="$PWD/config/features/Duender-CoreXY.json"
bash scripts/ci/generate-config.sh
```

Absolute tram corners are applied from `patches/bed_tramming.cpp` by `scripts/ci/patch_marlin_outputs.py`.

The script also copies `Version.h`, applies Marlin 2.1.3 `ANY`/`ALL` macro updates, and sets the **512K GD32 Neo** profile in `platformio.ini` (Mriscoc env `STM32F103RE_creality` — see [board-mcu.md](board-mcu.md)).

**Manual alternative:**

Copy `config/features/Duender-CoreXY.json` into `upstream/Special_Configurations/_features/`, then:

```bash
cd upstream/Special_Configurations
python3 -c "import CreateConfigs; CreateConfigs.Generate('Duender-422-BLTUBL-MPC-T13', ['Ender3V2','422','BLT','UBL','MPC','T13','Duender-CoreXY'])"
```

Copy outputs into the firmware tree:

| From generated folder | To |
|-----------------------|-----|
| `Configuration.h` | `Ender3V2S1/Marlin/Configuration.h` |
| `Configuration_adv.h` | `Ender3V2S1/Marlin/Configuration_adv.h` |
| `Version.h` | `Ender3V2S1/Marlin/Version.h` |
| `platformio.ini` | `Ender3V2S1/platformio.ini` |

### CI builds

Every push to `main` runs [.github/workflows/build-firmware.yml](../.github/workflows/build-firmware.yml). Download `Duender-422-BLTUBL-MPC-T13-CoreXY-0.1.0-beta.3.bin` from workflow **Artifacts**. CI uses measured geometry from `Duender-CoreXY-CI.json` (including probe-reachable UBL mesh) — verify travel limits on your frame before trusting a first print.

## 3. Apply manual edits

Work through [config/Configuration.h.diff-outline.md](../config/Configuration.h.diff-outline.md):

- Bed dimensions (after measuring)
- `NOZZLE_TO_PROBE_OFFSET`
- Motor invert flags after direction tests
- Optional: raise `DEFAULT_MAX_ACCELERATION` gradually after Input Shaping

## 4. Compile

**Board:** Creality 4.2.2 with **GD32F303RET6** (Ender-3 V2 Neo donor). Read [board-mcu.md](board-mcu.md) before choosing a build target — wrong flash size can brick the board.

```bash
cd upstream/Ender3V2S1   # or $FIRMWARE_DIR
pio run -e STM32F103RE_creality   # Mriscoc 512K env name — required for GD32F303RET6 Neo
```

### Build environment (GD32F303RET6 Neo)

Your **physical MCU** is GigaDevice **GD32F303RET6** (512 KB). Mriscoc names the required profile `STM32F103RE_creality` — that is the **PlatformIO environment name**, not the chip on the PCB.

| Physical MCU | PlatformIO env | Flash | Use for this project? |
|--------------|----------------|-------|------------------------|
| **GD32F303RET6** (Neo 4.2.2) | `STM32F103RE_creality` | 512 KB | **Yes — required** |
| STM32F103RCT6 | `STM32F103RC_creality` | 256 KB | **No — wrong size** |
| GD32F303 (maple env) | `GD32F303RE_creality_maple` | — | **No — ProUI build fails** |

Do **not** flash RC (256K) firmware on a GD32F303RET6 Neo board.

## 5. Flash

### SD card (typical)

1. Rename firmware to a unique `*.bin` (e.g. `Duender-beta-20260706.bin`).
2. Copy to FAT32 microSD root (≤32 GB, quality card).
3. Power off, insert card, power on.
4. Flash takes ~30 s; screen may go blank — wait for reboot.

### STM32 DFU / serial

Follow [Mriscoc install wiki](https://github.com/mriscoc/Ender3V2S1/wiki/How-to-install-the-firmware) if SD update fails.

## 6. Post-flash calibration

Order recommended by Mriscoc:

1. **MPC** autotune (hotend + bed) — save (`M500`)
2. **Probe Z-offset** — paper test or feeler, `M851 Z`, `M500`
3. **UBL** — `G29 P1` / wizard, `M500`
4. **E-steps** — extrusion test starting from `424.9`, `M92 E…`, `M500`
5. **Input Shaping** (if enabled in your branch) — resonance test, save
6. **Linear Advance** — tower test if `LA` feature enabled

## 7. Store settings in repo (optional)

Export working EEPROM values to a text snippet in `config/saved-settings/` for rebuilds — **never** commit machine-specific mesh blobs unless you intend to.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Axis runs wrong way on homing | `INVERT_X_DIR` / `INVERT_Y_DIR` |
| Diagonal moves only, no pure X/Y | `COREXY` not enabled |
| Z motors fight each other | Parallel wiring phase match; mechanical sync |
| Probe error / deploy fail | CR Touch on BL_T port; 5V not 3.3V |
| UI blank after flash | Wrong display profile — keep `Ender3V2` base, don't swap to S1 UI |
| Temps max out at 275 | Confirm `T13` profile; `HEATER_0_MAXTEMP 300` |
| Build fails config version | Use `Special_Configurations` **`main`**, not legacy `T13` tag |
| `DEFAULT_bedKp` compile error | Regenerate with current `Duender-CoreXY*.json` overlays |
| Wrong MCU profile / blank screen after flash | Confirm **GD32F303RET6** Neo board; use `STM32F103RE_creality` only — see [board-mcu.md](board-mcu.md) |
| Windows path / pins errors | Clone to `C:\fw` or `subst W:` short path |
