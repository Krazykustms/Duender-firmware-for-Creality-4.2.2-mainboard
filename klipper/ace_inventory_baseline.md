# ACE Gen1 inventory — baseline + measured

Fill remaining rows in [ace-mechanics-mmu.md](ace-mechanics-mmu.md). Anycubic FilamentBox + USBHUB abandoned for control.

## Motors (measured 2026-07-15)

| Motor | Type | Coil R | Notes |
|-------|------|--------|-------|
| **FEED** | bipolar stepper | **~2.6 Ω / pair** | Belt / drive wheels |
| **SEL** | bipolar stepper | **~2.6 Ω / pair** | Selector (black 6-pin labeled) |

### 6-pin plug layout (same on FEED and SEL)

4 wires, empties between each coil’s legs:

```
Pin:  1     2     3     4     5     6
     [ A ] [ · ] [ A ] [ B ] [ · ] [ B ]
       a           ab mids           b
```

| Coil | Pins | To driver |
|------|------|-----------|
| A | 1 + 3 | A+ / A− |
| B | 4 + 6 | B+ / B− |
| NC | 2 + 5 | leave open |

Start driver current ~0.5–0.8 A (low-Z coils).

| Item | Expected | Status |
|------|----------|--------|
| Gate sensors | OUTPUT strip + harness | keep mounted; pins reserved |
| Buffer Hall | buffer / assist | TBD wire |
| ZERO Hall | Neo Z-STOP `PA7` | verified with SEL home |
| NFC | ignore | skipped |
| Dryer fans | K-FAN1+K-FAN2 → `ace:PA0` | verified |
| Dryer PTC heaters | HE0=`ace:PA1`, HB=`ace:PA2` (non-polar screws) | open-loop PWM; chamber NTCs |
| Dryer NTC 1 / 2 | TH0=`ace:PC5`, TB=`ace:PC4` | ambient OK |
| FilamentBox board | abandoned | shelves |
| USBHUB | abandoned | shelves |

## Wiring target (this repo)

| Function | Klipper object | MCU |
|----------|----------------|-----|
| Gear / feed | `manual_stepper mmu_gear` | `[mcu ace]` (X driver) |
| Selector | `manual_stepper mmu_selector` | `[mcu ace]` (Z driver + PA7 endstop) |
| Gates 0–3 | `filament_switch_sensor mmu_gate_*` | `[mcu ace]` (pins reserved) |
| Dryer fans | `fan_generic ace_dryer_fan` | `[mcu ace]` PA0 |
| Heater 1 / 2 | `output_pin ace_heater1/2` | HE0 PA1 / HB PA2 |
| Thermistor 1 / 2 | `temperature_sensor ace_thermistor1/2` | TH0 PC5 / TB PC4 |
| Toolhead sensor | `filament_switch_sensor toolhead_sensor` | printer `[mcu]` (not enabled) |
| Cutter | `servo mmu_cutter` | printer `[mcu]` (not enabled) |

## MCU assignment

- Printer motion / Sprite / bed / CR Touch: **STM32F103RCT6** already on Pi.
- ACE actuators: flash idle **GD32 Neo** (or buy AFC Lite / MMB) as `[mcu ace]`.
