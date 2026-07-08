# Board and MCU — Creality 4.2.2 (Ender-3 V2 Neo donor)

This project targets a **specific physical board**, not a generic “STM32 printer.”

## Your hardware (this repo)

| Item | Value |
|------|--------|
| **Donor printer** | Ender-3 V2 Neo |
| **Mainboard** | Creality **4.2.2** (`BOARD_CREALITY_V4`) |
| **MCU** | **GD32F303RET6** (GigaDevice, 512 KB flash) — typical on Neo 4.2.2 |
| **Probe** | CR Touch |
| **Extruder** | Creality Sprite (`T13` thermistor) |
| **Display** | Stock Ender-3 V2 / Neo DWIN (Mriscoc ProUI) |

Some older 4.2.2 boards use **STM32F103RET6** (also 512 KB). This repo is validated for the **Neo GD32** donor stack. If you have a confirmed STM32 RET6 board, the same 512K Mriscoc profile usually applies — but verify the chip silkscreen before flashing.

## Mriscoc build environment (name ≠ chip)

Mriscoc and PlatformIO use legacy ST part numbers in **environment names**. That is a toolchain label, not a claim about the chip on your PCB.

| Physical board | Required PlatformIO env | Flash size |
|----------------|-------------------------|------------|
| **GD32F303RET6** (Neo 4.2.2 — **this project**) | `STM32F103RE_creality` | **512 KB** |
| STM32F103RET6 (rare 4.2.2 RET6) | `STM32F103RE_creality` | **512 KB** |
| STM32F103RCT6 (256K 4.2.2 only) | `STM32F103RC_creality` | 256 KB — **wrong for Neo** |

Compile command (env name only):

```bash
pio run -e STM32F103RE_creality
```

## Do not use these targets

| Target / config | Why |
|-----------------|-----|
| `STM32F103RC_creality` | **256K** profile — wrong flash size for GD32F303RET6 / Neo RET6 boards; can brick or behave badly |
| `GD32F303RE_creality_maple` | ProUI prebuild scripts fail on current Mriscoc builds |
| `Ender3S1` CreateConfigs tags | Wrong board, display, and pin map — **not** your Neo donor |
| Stock S1 firmware binaries | Incompatible with 4.2.2 + DWIN Neo UI |

## How to confirm your MCU

Before flashing any `.bin`:

1. Power off, read the MCU silkscreen on the 4.2.2 board (e.g. **GD32F303RET6**).
2. Confirm mainboard revision is **4.2.2** (not 4.2.7 F4, not S1 board).
3. Build or download firmware built with **`STM32F103RE_creality`** only (512K profile).
4. Rename the `.bin` uniquely before SD flash (Creality bootloader requirement).

## Why docs still mention “STM32F103RE”

Only because **Mriscoc names the build that way**. When you see `STM32F103RE_creality` in this repo, read it as:

> **512K Creality 4.2.2 firmware profile for GD32F303RET6 Neo boards**

—not “my board must contain an STM32F103.”
