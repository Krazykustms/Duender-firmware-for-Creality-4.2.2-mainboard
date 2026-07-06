# Duender PIN v6 (MGN9H) — Mriscoc Professional Firmware

Custom [Mriscoc Professional](https://github.com/mriscoc/Ender3V2S1) firmware for a **Duender PIN v6 MGN9H** CoreXY conversion.

**Goal:** Reuse the **Creality 4.2.2** mainboard from an **Ender-3 V2 Neo** (GD32F303RET6 or STM32F103RET6), keeping the **CR Touch**, **Sprite extruder**, and **DWIN display/UI** — while running CoreXY kinematics on the Duender frame. Dual Z steppers are wired in parallel on one driver.

**Repo:** [github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard](https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard)

[![Build firmware](https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard/actions/workflows/build-firmware.yml/badge.svg)](https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard/actions/workflows/build-firmware.yml)

Builds on the Mriscoc `Ender3V2-422-BLTUBL-MPC` profile + `T13` (Sprite thermistor) + `Duender-CoreXY` overlay.

**Contributing:** see [CONTRIBUTING.md](CONTRIBUTING.md). Download CI-built `.bin` files from the [Actions](https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard/actions) tab (artifacts use placeholder bed dimensions until you measure yours).

## Hardware summary

| Item | Detail |
|------|--------|
| **Your printer (donor)** | **Ender-3 V2 Neo** — 4.2.2 board, CR Touch, Sprite extruder |
| **Target machine** | Duender PIN v6 MGN9H CoreXY |
| Kinematics | CoreXY |
| Mainboard | Creality 4.2.2 (`BOARD_CREALITY_V4`) |
| MCU | GD32F303RET6 (STM32F103-compatible; same firmware target) |
| Probe | CR Touch (BLTouch-compatible) |
| Extruder | Creality Sprite (direct drive) → use **`T13`** thermistor profile |
| Z axis | Dual leadscrew steppers, **parallel-wired** to Z driver |
| Display | Stock Ender-3 V2 / Neo DWIN (Mriscoc UI) |

### Why does the repo say “Ender3V2S1”?

**You are not using an Ender-3 S1.** Names in this project refer to *Mriscoc’s upstream project*, not your donor printer:

| Name you see | What it actually means |
|--------------|------------------------|
| [mriscoc/**Ender3V2S1**](https://github.com/mriscoc/Ender3V2S1) | GitHub repo for **all** Mriscoc Professional firmware (V2, **V2 Neo**, S1, etc.) |
| CreateConfigs tag **`Ender3V2`** | Printer family: V2 / **V2 Neo** DWIN display + Creality UI — **this is yours** |
| CreateConfigs tag **`422`** | 4.2.2 mainboard pin map — **this is yours** |
| CreateConfigs tag **`T13`** | Sprite / Sprite Pro hotend thermistor (type 13) — **use this** even if Neo shipped with Sprite |
| CreateConfigs tag **`Ender3S1`** | ❌ Wrong — different board, different display, different pins |

Prebuilt binary you may already run: `Ender3V2-422-BLTUBL-MPC`. For Duender + Sprite thermistor, generate **`Ender3V2-422-BLTUBL-MPC-T13`** + `Duender-CoreXY`.

**Do not** use S1 firmware or `Ender3S1` configs on a V2 Neo — the pins and display protocol differ.

## Repository layout

```
.
├── README.md
├── docs/
│   ├── wiring.md              # Harness, driver slots, probe, power
│   └── build.md               # Compile and flash workflow
├── .github/
│   ├── workflows/build-firmware.yml        # PlatformIO CI
│   ├── ISSUE_TEMPLATE/                     # Bug, build, config help
│   └── pull_request_template.md
├── config/
│   ├── Configuration.h.diff-outline.md   # What to change vs stock Mriscoc base
│   └── features/
│       ├── Duender-CoreXY.json             # Your measured values (___MEASURE___)
│       └── Duender-CoreXY-CI.json          # CI-safe placeholder dimensions
├── scripts/ci/generate-config.sh           # Local + CI config generator
├── CONTRIBUTING.md
└── .gitignore
```

Firmware sources are **not vendored** here. Clone [mriscoc/Ender3V2S1](https://github.com/mriscoc/Ender3V2S1) and apply configs from this repo.

## Quick start

1. Read [docs/wiring.md](docs/wiring.md) and verify harness against your build.
2. Generate a base config from [mriscoc/Special_Configurations](https://github.com/mriscoc/Special_Configurations):

   ```python
   import CreateConfigs
   CreateConfigs.Generate(
       'Duender-422-BLTUBL-MPC-T13',
       ['Ender3V2', '422', 'BLT', 'UBL', 'MPC', 'T13', 'Duender-CoreXY']
   )
   ```

   Place `Duender-CoreXY.json` in `_features/` before running (see [config/features/](config/features/)).

3. Apply remaining edits from [config/Configuration.h.diff-outline.md](config/Configuration.h.diff-outline.md) — especially bed size, probe offset, and motor directions after first homing tests.
4. Build and flash per [docs/build.md](docs/build.md).

## Base configuration

Starting point: **Ender3V2-422-BLTUBL-MPC**

| Feature | Tag | Notes |
|---------|-----|-------|
| Board 4.2.2 | `422` | Creality V4 pin map |
| CR Touch | `BLT` | BLTouch-compatible probing |
| Bed leveling | `UBL` | Unified Bed Leveling |
| Hotend tuning | `MPC` | Model Predictive Control |
| Sprite thermistor | `T13` | Sensor type 13, 300 °C capable |

## Measurements still required

Fill these in after assembly (tracked in the diff outline):

- [ ] `X_BED_SIZE` / `Y_BED_SIZE` — usable print area
- [ ] `X_MAX_POS` / `Y_MAX_POS` — travel limits after homing
- [ ] `Z_MAX_POS` — mechanical Z travel (Duender builds often land near **~280 mm**; measure yours)
- [ ] `NOZZLE_TO_PROBE_OFFSET` — CR Touch mount on your toolhead
- [ ] `INVERT_X_DIR` / `INVERT_Y_DIR` — set after first CoreXY direction test

## References

- [Duender mechanical repo](https://github.com/Irbis3D/Duender)
- [Duender MGN9H on Printables](https://www.printables.com/model/1300968-duender-mgn9h-2x-creality-ender-3-corexy-convertio)
- [Mriscoc Ender3V2S1 wiki](https://github.com/mriscoc/Ender3V2S1/wiki)
- [Mriscoc calibration guides](https://github.com/mriscoc/Ender3V2S1/wiki/Calibration-Guides)
- [Duender Discord](https://discord.gg/ae44FHv786)

## License

GPL-2.0 (see [LICENSE](LICENSE)). Aligns with [Marlin](https://github.com/MarlinFirmware/Marlin), [Mriscoc Professional](https://github.com/mriscoc/Ender3V2S1), and [Duender](https://github.com/Irbis3D/Duender) (all GPL-2.0).