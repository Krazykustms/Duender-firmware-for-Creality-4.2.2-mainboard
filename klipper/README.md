# Klipper on Duender (BTT Pi host)

Live stack:

| Role | Board | Notes |
|------|--------|------|
| **Printer MCU** | Creality 4.2.2 **STM32F103RCT6** | Motion, Sprite, bed, CR Touch |
| **ACE MCU** | Creality 4.2.2 **GD32F303 Neo** | FEED/SEL, dryer, gate sensors |
| **Host** | BTT Pi | Klipper / Moonraker / Mainsail |

**ACE status hub:** [ACE-STATUS.md](ACE-STATUS.md)

## Config on the Pi

Copy (or sync) into `/home/biqu/printer_data/config/`:

- `printer.cfg` — CoreXY Duender + includes
- `ace_mmu.cfg`, `ace_dryer.cfg`, `ace_validate.cfg`
- `macros.cfg`, `calibrations.cfg`
- Optional later: `ace_toolhead.cfg`, Happy Hare `mmu/base/*.cfg`

Both boards share CH340 USB IDs — lock serials with **by-path** (already set in repo configs).

```bash
ls -l /dev/serial/by-path/
# Mainsail / console:
FIRMWARE_RESTART
```

## Flash notes

- Printer STM32 (broken SD): [FLASH-STLINK.txt](FLASH-STLINK.txt), `mcu-stm32f103-usart1-noboot.config`
- ACE GD32 Neo (512K): [ace_mcu_flash.md](ace_mcu_flash.md), [HARDWARE-SWITCH.md](HARDWARE-SWITCH.md)

## ACE path (summary)

Anycubic USB / FilamentBox control abandoned. Drive Gen1 mechanics from Klipper + Happy Hare **Custom**.

1. Motors / ZERO / dryer fans — done (see ACE-STATUS)
2. Gate sensors → Happy Hare → toolhead cutter → Orca multi-tool

## Reference

- [ace-mechanics-mmu.md](ace-mechanics-mmu.md) — full plan
- [duender-corexy.cfg](duender-corexy.cfg) — CoreXY reference snippets
