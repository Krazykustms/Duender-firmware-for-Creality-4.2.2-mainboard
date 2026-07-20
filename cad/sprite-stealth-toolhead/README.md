# Custom Sprite “Stealth” toolhead — Duender MGN9H

**Goal:** Rearrange Creality Sprite + CR Touch so the toolhead is **not front-heavy**, with a Stealthburner-like cowl — **without** changing the Creality 4.2.2 board or adding a Voron toolhead PCB.

**Status:** Design brief / CAD kickoff  
**References:**
- Sprite assembly STEP: `Downloads\...\Sprite_extruder_assembly.step`
- Carriage: **standard HIWIN-style MGN9H block** (not a custom printed plate)
- Drop stock part: `PCB_fan_shroud_print_head_gantry_bracket_ASM_001` (front cantilever plate)

## Constraints (keep)

| Item | Keep |
|------|------|
| Mainboard | Creality 4.2.2 (GD32) — wiring unchanged |
| Extruder | Sprite DD (NEMA17 42-26 + gearbox) |
| Probe | CR Touch (rewire same BL_T header) |
| Hotend | Sprite throat / block / T13 thermistor |
| Carriage | **MGN9H** — 4× M3 on **15 × 16 mm** centers |

### Standard MGN9H block (HIWIN)

| Dim | Value |
|-----|--------|
| Block W × L × H | 20 × 39.9 × 10 mm |
| Hole pattern B × C | **15 × 16 mm** |
| Threads | M3 × 4 (depth ~3 mm — use short screws / don’t bottom out) |

Adapter plate bolts **down onto** the MGN9H; Sprite gearbox bolts **onto** the adapter.

No Stealthburner PCB / Cordatus / etc. required. Fans can stay on board PWM headers.

## Layout (target)

```
     rear
       ↑
   [Sprite motor]
   [gearbox   ]     ← CG over / slightly behind rail
   ──── MGN9H ────
   [hotend drop]
   [printed cowl]   ← ducts + CR Touch pocket (light)
       ↓
     front
```

### Mass rules
1. Motor + gearbox sit **above the carriage** (not ahead of it).
2. Cowl is plastic only — fans, ducts, probe.
3. Probe preferably **side or high on cowl**, not a long front stick — shorten XY offset vs current `{-31,-39}` if possible.

## Printable parts (v1)

| Part | Job |
|------|-----|
| `carriage_adapter` | MGN9H carriage → Sprite gearbox mounts |
| `main_body` | Ties adapter, heatsink clamp, cowl screws |
| `cowl_front` | Part-cooling ducts + aesthetic shell |
| `probe_mount` | CR Touch on cowl (adjustable slots useful) |
| `cable_cover` (optional) | Strain relief toward chain |

Reuse Sprite stock: motor, gearbox, heatsink, heatbreak, block, nozzle, 3010/4010 fans if they fit.

## CAD workflow (Fusion / FreeCAD)

1. Place a **15 × 16 mm** M3 rectangle as origin (top of MGN9H).
2. Import `Sprite_extruder_assembly.step` — **hide/suppress** gantry bracket.
3. Rotate/translate Sprite so:
   - Nozzle on machine −Z
   - Motor toward **rear**
   - Gearbox screws land on adapter bosses above the rail
4. Sketch `carriage_adapter` from MGN9H holes + Sprite gearbox hole pattern.
5. Shell `main_body` + `cowl` around heatsink / fans.
6. Place CR Touch; export probe tip vs nozzle → new `NOZZLE_TO_PROBE_OFFSET`.

Starter blank plate: `mgn9h_adapter_blank.scad` (MGN9H holes only).

## Firmware follow-up (after install)

Remeasure and update:
- `NOZZLE_TO_PROBE_OFFSET`
- `MESH_MIN/MAX_*` (probe reach)
- Tram auto corners in `patches/bed_tramming.cpp`
- Orca printable polygon if nozzle travel changes

## Non-goals (v1)

- Voron Clockwork 2 / toolhead PCB
- Board swap / Klipper
- Perfect Stealthburner cosmetics (function first)

## Next concrete step

Measure or export from CAD:
1. MGN9H carriage screw pattern (centers)
2. Sprite gearbox → mount hole pattern (from STEP, without stock bracket)
3. Nozzle position relative to carriage face

Then model `carriage_adapter` only and dry-fit before cowl.
