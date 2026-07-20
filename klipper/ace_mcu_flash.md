# Duender ACE MCU (second Klipper MCU) — flash notes

The live printer already uses the **STM32F103RCT6** board. ACE motors/sensors need a **second** USB MCU:

**Preferred:** idle Duender **GD32F303RET6 Neo** board (512K Flash) — was Marlin.

## SD flash (preferred for working SD slot)

Config: [`mcu-gd32f303-usart1-28k.config`](mcu-gd32f303-usart1-28k.config)  
Prebuilt on Pi / repo: `klipper-gd32f303-neo-28k-sd.bin`

| Setting | Value |
|---------|--------|
| Chip | STM32F103xE (512K) — matches GD32F303RET6 Neo |
| Bootloader | **28KiB** (Creality SD) |
| Serial | USART1 PA10/PA9 → CH340 |
| Crystal | 8 MHz |

1. Copy **`firmware-ACE-gd32.bin`** to SD card **root** (unique name so bootloader reflash).
2. Power **off** Neo board → insert SD → power **on** (USB or 24V).
3. Wait ~10–20 s (CH340 may drop/reconnect).
4. Power off → **remove SD** → power on again.
5. Laptop Device Manager / Pi: CH340 still present; after Klipper host connect it becomes `/dev/serial/by-id/usb-1a86_...` or Klipper-named id.

```bash
# Rebuild on Pi if needed
cd ~/klipper
cp ~/printer_data/config/mcu-gd32f303-usart1-28k.config .config
make olddefconfig && make clean && make -j4
cp out/klipper.bin ~/printer_data/config/klipper-gd32f303-neo-28k-sd.bin
```

## ST-Link (if SD fails)

Use **No bootloader** build and flash at `0x08000000` (see [FLASH-STLINK.txt](FLASH-STLINK.txt)). Then:

```bash
ls -l /dev/serial/by-id/
# Put that path into ace_mmu.cfg → [mcu ace] serial:
```

## Drivers on that board

Treat it as a **Creality V4 pinout** spare: use the **E** driver for `mmu_gear`, **Z** (or X) driver for `mmu_selector` if the clutch is a stepper. Gate sensors on endstop pins. Do **not** connect bed/hotend heaters on the ACE MCU for normal use.

## Alternative

Buy **AFC Lite / MMB / SKR Pico** as `[mcu ace]` — same `ace_mmu.cfg` pattern, different pin names in Happy Hare hardware file.
