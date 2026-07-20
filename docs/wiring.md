# Wiring notes — Duender MGN9H on Creality 4.2.2

Wiring map for this firmware repo. Pin names follow Marlin `pins_CREALITY_V4.h` (4.2.2 / 4.2.7 family).

> **MCU (read first):** This repo targets **GD32F303RET6** on Creality **4.2.2** (Ender-3 V2 Neo). Pin map follows `pins_CREALITY_V4.h`. Build with Mriscoc env **`STM32F103RE_creality`** (512K profile name only). See [board-mcu.md](board-mcu.md) — **do not** flash 256K (`RC`) firmware on Neo GD32 boards.

## Driver slot assignment (Duender CoreXY)

The 4.2.2 board has four integrated TMC2225 drivers. On CoreXY, **firmware X/Y axes map to belt motors**, not cartesian gantries.

| Board label | Marlin axis | Duender function | Cable |
|-------------|-------------|------------------|-------|
| **X** | `X` | CoreXY motor **A** (X+Y belt) | 4-pin motor, Duender XY harness |
| **Y** | `Y` | CoreXY motor **B** (X−Y belt) | 4-pin motor, Duender XY harness |
| **Z** | `Z` | **Both** Z steppers (parallel) | Y-splitter or spliced harness → single Z port |
| **E** | `E0` | Sprite extruder stepper | Sprite motor extension cable |

### Dual Z in parallel (one driver)

Both Z motors share the **Z** driver socket:

- Wire **step**, **dir**, and **enable** in parallel (A+/A− and B+/B− matched per motor).
- Use identical motors and leadscrew pitch.
- **No second Z driver** — do **not** enable `NUM_Z_STEPPER_DRIVERS` / `Z_STEPPER_ALIGN` unless you add a second driver later.
- Level the bed mechanically (couplers, shims, or one-time gantry trim) before relying on mesh/UBL.

```
Z driver (4.2.2)          Motor L          Motor R
  STEP  ────────────────┬─────── STEP
  DIR   ────────────────┼─────── DIR
  EN    ────────────────┴─────── EN
  A+/A− ─── motor L ───
  B+/B− ─── motor R ───
```

## Stepper signal pins (4.2.2 reference)

| Axis | STEP | DIR | ENABLE (shared) |
|------|------|-----|-----------------|
| X | PC2 | PB9 | PC3 |
| Y | PB8 | PB7 | PC3 |
| Z | PB6 | PB5 | PC3 |
| E0 | PB4 | PB3 | PC3 |

If an axis moves the wrong way, fix it in firmware first with `INVERT_*_DIR`.

For this specific Duender conversion, Z direction is already a known **firmware-only** item: keep the current Z wiring as-is. With the current cartesian-baseline Mriscoc setup, positive Z drives the bed **up** when final Duender behavior should drive the bed **down**. Correct this by flipping `INVERT_Z_DIR` in the final CoreXY build, then verify with a small safe `Z+` jog before trusting homing or probing.

## Endstops

Stock Ender-3 style **NC switches to GND** (pull-up enabled in firmware).

| Function | Typical 4.2.2 pin | Duender |
|----------|-------------------|---------|
| X min | PA5 | Front-left X home switch |
| Y min | PA6 | **Front-left** Y home switch (move from rear for standard Marlin coords) |
| Z min | PA7 | **Not used for homing** when CR Touch probes Z |

Duender uses **COREXY** with **both inverts true** (`INVERT_X_DIR` / `INVERT_Y_DIR`). With the Y switch at **front-left**, use `Y_HOME_DIR -1` and **normal motor plugs** — X motor on the **X** driver, Y motor on the **Y** driver (not swapped). Validated flash baseline: **`D025.bin`**. Do **not** flip a single motor plug 180° on CoreXY.

**Probe XY offset:** `NOZZLE_TO_PROBE_OFFSET { -31, -39, 0 }` — probe is 31 mm left and 39 mm **in front** of the nozzle (negative Y in Marlin). After any probe-offset flash: `M502` then `M500`, then re-set Z offset.

**Bed / print (measured D025):**

| Region | Min | Max |
|--------|-----|-----|
| Bed travel | X0 Y0 | X201 Y235 |
| Print area (nozzle) | X1 Y23 | X200 Y234 |
| UBL mesh (probe tip) | X10 Y23 | X170 Y196 |

**Tramming (two coordinate sets in `patches/bed_tramming.cpp`):**

| Mode | When | FL | FR | BR | BL |
|------|------|----|----|----|----|
| **Manual** | ProUI “Manual Tramming” ON — nozzle at screws | 1,22 | 201,22 | 201,235 | 1,235 |
| **Auto / probe** | Manual OFF / Tramming Wizard — probe tip | 19,61 | 170,61 | 170,196 | 19,196 |

Auto coords are **probe tip** positions and are **clamped at runtime** to `probe.min/max ± 3 mm` so ProUI Physical Settings / EEPROM can’t push FR past reach. Typical reach with `{ -31, -39, 0 }` is about **X 10–170, Y 10–196**. Mesh must use that reach — do not set UBL to the full nozzle print rectangle.

## CR Touch (BL_T port)

Connect to the dedicated **BLTouch** header on 4.2.2:

| CR Touch wire | 4.2.2 / Marlin | Notes |
|---------------|----------------|-------|
| Brown / GND | GND | |
| Red / +5V | 5V | |
| Orange / yellow control | PB0 (`SERVO0`) | Deploy/stow |
| White / signal | **PB1** (`Z_MIN_PROBE_PIN`) | Probe trigger on **BL_T** 5-pin |

**Not PA7** — that is `Z_STOP_PIN` (mechanical Z endstop). Marlin `pins_CREALITY_V4.h`: `SERVO0_PIN PB0`, `Z_MIN_PROBE_PIN PB1`, `Z_STOP_PIN PA7`. Klipper: `control_pin: PB0`, `sensor_pin: ^PB1`.

Firmware: `#define BLTOUCH` (already in BLTUBL base). Z homing uses probe via `Z_SAFE_HOMING` at bed center — same as stock Mriscoc CRTouch builds.

**Mounting:** Measure and set `NOZZLE_TO_PROBE_OFFSET { x, y, z }` after installing the probe on your Duender toolhead. If you are still using the stock Ender carriage / Sprite / CR Touch layout, stock Ender offsets are a reasonable **starting point** only; confirm final values on your assembled Duender.

## Sprite extruder

| Function | 4.2.2 terminal | Notes |
|----------|----------------|-------|
| E stepper | E driver (above) | |
| Hotend heater | E0 heater screw terminal | |
| Hotend thermistor | TH0 | Use sensor **type 13** (`T13` profile) |
| Part cooling fan | FAN0 | |
| Hotend fan | FAN1 (always-on in firmware) | |

**E-steps starting value:** `424.9` mm⁻¹ (Creality Sprite reference). Calibrate with a 120 mm extrusion test; store with `M500`.

**Thermistor:** Sprite / Sprite Pro → `TEMP_SENSOR_0 13` (100k β3950, 300 °C max in T13 profile).

## Heated bed

| Function | Terminal |
|----------|----------|
| Bed heater | Bed HE |
| Bed thermistor | TB |

Stock Ender thermistor type **1** (100k EPCOS) unless you changed the sensor.

## Display (keep Mriscoc UI)

Leave the **stock Ender-3 V2 DWIN** ribbon on **EXP1 / EXP3** as on the original Ender-3 V2. No wiring change required for Mriscoc Professional.

| Setting | Value |
|---------|-------|
| `SERIAL_PORT` | `1` (USART1 — display channel on Creality V4) |
| `BAUDRATE` | `250000` |

## Power and safety

- **Mains:** Use the original Creality PSU or equivalent 24 V supply sized for bed + hotend + three XY motors.
- **Power off** for all harness work.
- **Probe + hotend fan + CR Touch** share the board's 5 V budget — use the Creality BL_T harness; avoid long unshielded probe runs parallel to stepper cables.
- **Frame ground:** Earth the PSU chassis to the frame per Duender / Ender practice.

## Pre-flight checklist

- [ ] XY motors on **X** and **Y** drivers (not Z/E)
- [ ] Both Z motors on **Z** driver only, phases matched
- [ ] Sprite on **E**, thermistor on **TH0**
- [ ] CR Touch on **BL_T** port (not endstop-only wiring)
- [ ] X/Y endstops hit **before** carriage crashes at front-left
- [ ] Bed thermistor and heater secure — no strain on screw terminals
- [ ] Display ribbon seated; printer boots to Mriscoc UI

## First power-on (before trusting homing)

1. Power on; confirm UI and temperatures read sane.
2. Disable steppers; hand-move gantry to center.
3. `M119` — endstops idle **open**, triggered when pressed.
4. Home **X only** (`G28 X`) at low feedrate; verify direction toward X switch.
5. Home **Y only**; verify direction toward Y switch.
6. Fix `INVERT_X_DIR` / `INVERT_Y_DIR` if either axis runs away.
7. Deploy CR Touch (`M280 P0 S10` / LCD) before first **Z** home.
8. Before trusting probe motion, jog `Z+` a few millimeters and confirm the bed moves **down**.
9. Run `G28` full home; set probe Z-offset (`M851 Z`) and `M500`.
