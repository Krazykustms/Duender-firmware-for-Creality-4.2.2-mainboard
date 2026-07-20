# ACE Gen1 → Duender Klipper — status

**Host:** BTT Pi / Mainsail `http://192.168.1.235`  
**Goal:** Drive ACE Pro Gen1 mechanics from Klipper + Happy Hare Custom (no Anycubic USB/FilamentBox).

## MCU map

| Role | Board | Config |
|------|--------|--------|
| Printer | STM32F103RCT6 Creality 4.2.2 | `[mcu]` in `printer.cfg` |
| ACE | GD32F303 Neo (ex-Marlin Duender) | `[mcu ace]` in `ace_mmu.cfg` |

Both CH340 USB IDs collide — use **by-path** serials (see `printer.cfg` / `ace_mmu.cfg`).

## Bring-up checklist

| Area | Status | Notes |
|------|--------|-------|
| Anycubic USB / FilamentBox / ValgACE | Abandoned | Do not power FilamentBox for logic |
| FEED + SEL steppers (~2.6 Ω) | Verified | FEED→X, SEL→Z on Neo; macros `ACE_GEAR_TEST` / `ACE_SEL_*` |
| ZERO Hall (SEL home) | Verified | Neo Z-STOP `PA7`; may need 5 V from BL_T V |
| Dryer fans K-FAN1/K-FAN2 | Verified | Shared MOSFET `ace:PA0` → `ace_dryer_fan` |
| Thermistor 1 / 2 | Verified | TH0=`ace:PC5`, TB=`ace:PC4` (~ambient OK) |
| Heater 1 / 2 PTC | Open-loop on HE0/HB | `ace:PA1` / `ace:PA2`; non-polar screw headers; chamber NTCs need lid+fans |
| Gate / buffer sensors | Pins reserved | Wire + `ACE_SENSOR_QUERY` next |
| Toolhead cutter + filament sensor | Config ready, not included | `ace_toolhead.cfg` commented in `printer.cfg` |
| Happy Hare | Not installed | See `ace_mmu_happy_hare.md` |
| Orca 4-tool | Notes only | Wait until HH load/unload works |

## Dryer (current)

Separate objects — open-loop PWM (no heater-verify fault):

| Label | Neo silk | Pin | Object |
|-------|----------|-----|--------|
| Thermistor 1 | TH0 | `ace:PC5` | `ace_thermistor1` |
| Thermistor 2 | TB | `ace:PC4` | `ace_thermistor2` |
| Heater 1 | HE0 (non-polar 24 V screws) | `ace:PA1` | `ace_heater1` |
| Heater 2 | HB (non-polar 24 V screws) | `ace:PA2` | `ace_heater2` |
| Fans | K-FAN1 + K-FAN2 | `ace:PA0` | `ace_dryer_fan` |

```gcode
ACE_DRYER_ON              ; fans 100% + heaters 75%
ACE_DRYER_ON POWER=0.5
ACE_DRYER_OFF
ACE_FAN_TEST
ACE_GEAR_TEST
ACE_SEL_HOME
ACE_SENSOR_QUERY
```

NTCs are **chamber air** — expect little rise with lid off. PWM average on a DMM (~18–19 V at 75%) is normal; check DC-IN ~24 V separately.

## Doc index

| File | Purpose |
|------|---------|
| [ace-mechanics-mmu.md](ace-mechanics-mmu.md) | Plan / phases |
| [ace_inventory_baseline.md](ace_inventory_baseline.md) | Measured motors + wiring targets |
| [ace_mmu.cfg](ace_mmu.cfg) | `[mcu ace]`, FEED/SEL, gates, test macros |
| [ace_dryer.cfg](ace_dryer.cfg) | Fans + dual heaters/thermistors |
| [ace_toolhead.cfg](ace_toolhead.cfg) | Cutter + toolhead sensor (not enabled yet) |
| [ace_mmu_happy_hare.md](ace_mmu_happy_hare.md) | HH Custom install choices |
| [ace_mcu_flash.md](ace_mcu_flash.md) | Flash Neo as second MCU |
| [../slicer/orcaslicer/ACE-MMU-NOTES.md](../slicer/orcaslicer/ACE-MMU-NOTES.md) | Orca multi-tool (after HH) |

## Next

1. Wire/validate gate sensors → `ACE_SENSOR_QUERY`
2. Install Happy Hare Custom (4 gates, gear MCU `ace`)
3. Enable `ace_toolhead.cfg` when cutter + sensor fitted
4. Orca 2-color then 4-color
