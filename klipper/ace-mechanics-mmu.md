# ACE Pro Gen1 mechanics → Klipper multicolor (no Anycubic OS)

Anycubic **USB / FilamentBox firmware / USBHUB** are abandoned for control. Keep the **mechanical box** (slots, drive wheels, belt, buffer, sensors, dryer shell) and drive it from Klipper + [Happy Hare](https://github.com/moggieuk/Happy-Hare) **Custom** MMU.

**Live status:** [ACE-STATUS.md](ACE-STATUS.md) (motors / ZERO / dryer fans verified; heaters open-loop; gates + Happy Hare next).

## Current Duender reality (important)

| Role | Board |
|------|--------|
| **Printer MCU (live)** | Spare **STM32F103RCT6** Creality 4.2.2 → Pi CH340 (`printer.cfg` `[mcu]`) |
| **Idle / available for ACE** | Duender **GD32F303 Neo** (was Marlin) — flash Klipper and use as **`[mcu ace]`** |
| Anycubic FilamentBox + USBHUB | **Do not power for logic**; trace connectors only |

The plan’s original “spare 4.2.2 as ACE MCU” is obsolete: that board **is** the printer. ACE actuators go on **`[mcu ace]`** (GD32 or any extra USB MCU / AFC Lite).

```
Orca T0–T3 → Happy Hare → printer MCU (extruder, cutter, toolhead sensor)
                        → [mcu ace] (feed stepper, selector, gate/buffer sensors)
```

## Phase 0 — abandoned path

- No ValgACE / BunnyACE until stock USB works again (not expected).
- Stop any `ace_watch` USB poll on the Pi.
- Leave Anycubic 3.3 V rails alone; do not inject voltage onto MCU pins.

---

## Phase 1 — electrical inventory worksheet

**Power off** ACE wall PSU. Unplug FilamentBox / hub from motor and sensor cables. Fill this table while metering.

### Expected Gen1 topology (from Anycubic docs)

- **Shared feed motor** (silver motor + belt → drive wheels) — usually **one** motor for all slots  
- **Slot engagement** — clutch / gate select (verify: second motor, solenoid, or cam)  
- **Per-slot filament presence** detectors (optical / switch / Hall)  
- **Buffer** slider + **Hall** (tangle / assist feedback)  
- NFC boards — **ignore** for v1  

### Motors

| ID | Connector silk | Wire count | Coil ohms (pairs) | Type (stepper/DC) | Role guess | Notes |
|----|----------------|------------|-------------------|-------------------|------------|-------|
| M1 | | | | | feed / gear | |
| M2 | | | | | selector / clutch | |
| M3 | | | | | | |

Stepper clue: 4 wires, two equal coil pairs. DC/solenoid: 2 wires.

### Sensors

| ID | Silk / location | Wire count | Type | Active level | Maps to Happy Hare |
|----|-----------------|------------|------|--------------|--------------------|
| S0 | slot 0 | | | | pre-gate / gate 0 |
| S1 | slot 1 | | | | gate 1 |
| S2 | slot 2 | | | | gate 2 |
| S3 | slot 3 | | | | gate 3 |
| BUF | buffer Hall | | | | sync / jam / espooler trig |

### Power rails (PSU only — not FilamentBox 3.3 V)

| Rail | Voltage | Use |
|------|---------|-----|
| ACE PSU motor / heater | measure | steppers / dryer later |
| Logic for Hall/optical | often 5 V or 3.3 V from **your** MCU/reg, not Anycubic LDO | sensors |

**Exit criteria:** actuator types known; pin budget on `[mcu ace]` known; if more steppers than drivers, add external TMC/A4988 or AFC Lite.

---

## Phase 2 — wire to `[mcu ace]`

1. Flash Klipper on the **GD32 Neo** (or other USB MCU). See [HARDWARE-SWITCH.md](HARDWARE-SWITCH.md) / ST-Link notes; use a **512K** build for GD32F303RET6.
2. USB that board to the BTT Pi (second serial).
3. Set `serial:` in [`ace_mmu.cfg`](ace_mmu.cfg) from `ls /dev/serial/by-id/`.
4. Power ACE **motors** from a measured safe rail (typically printer 24 V or ACE motor PSU after confirm).  
   **Do not** power Anycubic FilamentBox logic.
5. Map steps/dir/en + sensors into `ace_mmu.cfg` (placeholders marked `TODO_PIN`).

Include from `printer.cfg`:

```ini
[include ace_mmu.cfg]
[include mmu/base/*.cfg]   # after Happy Hare install
```

---

## Phase 3 — toolhead (Duender Sprite)

Multicolor needs **cut → retract → load**:

| Part | Wiring | Config |
|------|--------|--------|
| Filament cutter (servo or blade servo) | Free pin — **not** BLTouch `PB0` | [`ace_toolhead.cfg`](ace_toolhead.cfg) |
| Toolhead filament sensor | Endstop-style pin + pullup | same file |

Park / purge macros live in Happy Hare; cutter angle/time tuned there.

---

## Phase 4 — Happy Hare Custom

On the Pi:

```bash
cd ~
git clone https://github.com/moggieuk/Happy-Hare.git
cd Happy-Hare
./install.sh
```

Installer choices for this project:

- MMU type: **Custom / Other** (not BoxTurtle / ERCF preset unless inventory proves a perfect match)  
- Gates: **4**  
- Gear stepper MCU: **`ace`**  
- Selector: whatever inventory finds (stepper or DC via `output_pin`)

Bring-up order: `MMU_HOME` / gate select → load gate 0 to toolhead → unload → gate 1. **No Orca multi-tool until that works.**

Repo companion notes: [`ace_mmu_happy_hare.md`](ace_mmu_happy_hare.md).

---

## Phase 5 — slicer / validation

- Orca: 4 tools; toolchange → Happy Hare (`T` / `MMU_CHANGE_TOOL`) — see [`../slicer/orcaslicer/ACE-MMU-NOTES.md`](../slicer/orcaslicer/ACE-MMU-NOTES.md).
- Print: 2-color purge tower, then 4-color.
- Dryer: optional later via `[heater_generic]` once heater/thermistor pins are known — not required for toolchange.

## Fallback

If Gen1 clutch/selector cannot be driven reliably: keep ACE **shell + dryer**, replace internals with a known open 4-lane design (BoxTurtle-class). Same Happy Hare goal, more parts.
