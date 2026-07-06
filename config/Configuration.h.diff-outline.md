# Configuration.h diff outline — Duender CoreXY

Base profile: **`Ender3V2-422-BLTUBL-MPC`**  
Target: **Duender PIN v6 MGN9H** on Creality **4.2.2** + CR Touch + Sprite + parallel dual Z

Apply via [CreateConfigs.py](https://github.com/mriscoc/Special_Configurations) + `Duender-CoreXY.json`, then finish manual items below.

Legend: `→` = change from stock Ender3V2-422-BLTUBL-MPC value.

---

## Machine identity

```c
// CUSTOM_MACHINE_NAME
→ "Duender-MGN9H-422-BLTUBL-MPC"

// MOTHERBOARD — unchanged
#define MOTHERBOARD BOARD_CREALITY_V4   // 4.2.2
```

---

## Kinematics (critical)

```c
// @section machine — enable CoreXY
//#define COREXY
→ #define COREXY

// Leave CoreXZ / CoreYZ / MARKFORGED_* disabled
```

With `COREXY` enabled, Marlin maps:

- `X` stepper → board **X** driver (CoreXY motor A)
- `Y` stepper → board **Y** driver (CoreXY motor B)
- Pure X/Y motion uses both motors; tune directions together.

**Do not** change pin definitions unless you rewired drivers to non-stock slots.

---

## Extruder / hotend (Sprite + T13)

```c
// TEMP_SENSOR_0
#define TEMP_SENSOR_0 1
→ #define TEMP_SENSOR_0 13        // T13: Sprite / Sprite Pro (100k β3950)

// HEATER_0_MAXTEMP (with T13 overlay)
#define HEATER_0_MAXTEMP 275
→ #define HEATER_0_MAXTEMP 300    // verify hotend hardware limit

// DEFAULT_AXIS_STEPS_PER_UNIT { X, Y, Z, E }
#define DEFAULT_AXIS_STEPS_PER_UNIT { 80, 80, 400, 93 }
→ #define DEFAULT_AXIS_STEPS_PER_UNIT { 80, 80, 400, 424.9 }
//                                                      ^^^^^ Sprite reference — calibrate E

// INVERT_E0_DIR — verify after extruder test; may need toggle vs stock
```

---

## Motion limits (Duender — measure before shipping firmware)

```c
// DEFAULT_MAX_FEEDRATE { X, Y, Z, E }
// Conservative CoreXY starting point; raise after Input Shaping
→ #define DEFAULT_MAX_FEEDRATE { 300, 300, 25, 60 }
// (stock Ender3V2-422-BLTUBL-MPC is already 300/300/25/60 — OK to keep)

// DEFAULT_MAX_ACCELERATION { X, Y, Z, E }
// Duender MGN9H community reports ~18k real accel with IS; start lower
#define DEFAULT_MAX_ACCELERATION { 500, 500, 100, 1000 }
→ #define DEFAULT_MAX_ACCELERATION { 3000, 3000, 100, 1000 }
// tune upward after belt tension + input shaping calibration

// JERK / junction deviation — keep Mriscoc defaults unless you know you need changes
```

---

## Endstops and direction

```c
// Stock — keep unless your switches are mounted at MAX
#define USE_XMIN_PLUG
#define USE_YMIN_PLUG
#define USE_ZMIN_PLUG       // probe shares Z_MIN on 4.2.2

#define X_HOME_DIR -1
#define Y_HOME_DIR -1
#define Z_HOME_DIR -1     // homing via probe (Z_SAFE_HOMING), not mechanical Z-min

// INVERT_*_DIR — MUST verify on hardware; starting guess from Ender cartesian often wrong
#define INVERT_X_DIR false   // → toggle if X homes away from switch
#define INVERT_Y_DIR false   // → toggle if Y homes away from switch
#define INVERT_Z_DIR true    // usually keep Ender Z screw direction
#define INVERT_E0_DIR false  // → toggle if Sprite extrudes backward
```

**CoreXY direction test:** After `G28 X` / `G28 Y`, `G0 X10` should move nozzle +X; `G0 Y10` should move +Y. If you get mirroring, swap invert flags (only one axis may need flipping).

---

## Printable area (TBD — fill after measuring)

Duender uses two Ender frames; usable area is **not** 230×230 until you confirm.

```c
// @section geometry
#define X_BED_SIZE 230
→ #define X_BED_SIZE ___MEASURE___   // mm, usable print width

#define Y_BED_SIZE 230
→ #define Y_BED_SIZE ___MEASURE___   // mm, usable print depth

#define X_MIN_POS 0
#define Y_MIN_POS 0
#define Z_MIN_POS 0

#define X_MAX_POS 248
→ #define X_MAX_POS ___MEASURE___    // typically X_BED_SIZE + margin to physical stop

#define Y_MAX_POS 231
→ #define Y_MAX_POS ___MEASURE___

#define Z_MAX_POS 250
→ #define Z_MAX_POS ___MEASURE___    // Duender builds often ~270–280 mm; measure cold
```

**How to measure:**

1. Home X/Y (`G28 X Y`).
2. Jog nozzle to **opposite corner** of usable bed without crashing idlers into frame.
3. Read `M114` — that's your practical `X_MAX_POS` / `Y_MAX_POS`.
4. Set `X_BED_SIZE` / `Y_BED_SIZE` slightly **inside** those limits (probe reach, clip clearance).
5. UBL mesh bounds should stay inside bed size.

---

## Probe (CR Touch) — unchanged feature set, new offsets

```c
#define BLTOUCH                    // keep — CR Touch compatible

// NOZZLE_TO_PROBE_OFFSET { X, Y, Z }
#define NOZZLE_TO_PROBE_OFFSET { -41.5, -7, 0 }   // Ender stock mount
→ #define NOZZLE_TO_PROBE_OFFSET { ___X___, ___Y___, 0 }
// Measure: nozzle tip vs probe pin center when probe is deployed
// Set Z via babystep / M851 after G28 — the .z field is often 0 in config

#define Z_SAFE_HOMING              // keep
#define Z_SAFE_HOMING_X_POINT X_CENTER
#define Z_SAFE_HOMING_Y_POINT Y_CENTER

// AUTO_BED_LEVELING_UBL — keep from BLTUBL base
#define AUTO_BED_LEVELING_UBL
```

---

## Dual Z (parallel — no extra defines)

```c
// Do NOT enable unless you add a second Z driver:
// #define NUM_Z_STEPPER_DRIVERS 2
// #define Z_STEPPER_ALIGN

// Single Z driver, two motors in parallel — stock Z block unchanged:
// Z_STEP_PIN PB6, Z_DIR_PIN PB5, etc.
```

---

## Features kept from BLTUBL-MPC (no change expected)

```c
#define BLTOUCH
#define AUTO_BED_LEVELING_UBL
#define Z_SAFE_HOMING
#define HOME_AFTER_DEACTIVATE
#define THERMAL_PROTECTION_HOTENDS
#define THERMAL_PROTECTION_BED
// MPC settings live in Configuration_adv.h — keep MPC feature tag
```

---

## Optional enhancements (later)

| Feature | CreateConfigs tag | When |
|---------|-------------------|------|
| Input Shaping | `IS` | After basic motion verified |
| Linear Advance | `LA` | After extrusion calibrated |
| Higher jerk for CoreXY | manual in `Configuration_adv.h` | After IS tuned |

---

## Configuration_adv.h touchpoints

Check these after generating base config (values vary by Mriscoc release):

| Topic | Action |
|-------|--------|
| `MPC` hotend/bed constants | Re-run MPC tune on Duender (`M306 T`) |
| `TMC` currents | XY may need bump vs stock cartesian — set via LCD or `M906` |
| `INPUT_SHAPING_*` | Enable only with `IS` feature; tune X/Y separately |
| `UBL` slots / mesh | `GRID_MAX_POINTS_X/Y` — 10×10 is fine to start |
| `NOZZLE_PARK_POINT` | Update if bed dimensions change significantly |

---

## Validation G-code sequence

```gcode
M119                  ; endstops
G28                   ; full home
G0 X10 Y10 F3000      ; +X/+Y sanity
G0 X0 Y100            ; square diagonal
M851                  ; show probe offset
G29 P1                ; UBL probe (or use LCD wizard)
M500                  ; save
```

---

## Checklist before calling firmware "done"

- [ ] `COREXY` enabled
- [ ] `TEMP_SENSOR_0` = 13, Sprite E-steps calibrated
- [ ] Bed size / travel limits measured
- [ ] Probe offset measured for **your** CR Touch mount
- [ ] X/Y invert correct — no runaway homing
- [ ] Dual Z parallel — smooth Z travel, no binding
- [ ] UBL mesh stored (`M500`)
- [ ] MPC stored (`M500`)
- [ ] `CUSTOM_MACHINE_NAME` shows on boot screen
