# Bring-up status

**Status (2026-07-11):** firmware is **fully functional** for daily bring-up and first prints — **not motion/quality tuned**.

## Summary

Duender PIN v6 MGN9H CoreXY on Creality **4.2.2** (GD32 Neo) with Mriscoc ProUI is past motion bring-up. Jog, homing, tram, probe Z, UBL mesh (probe-reachable bounds), and an OrcaSlicer machine profile are working on hardware.

Still open: Input Shaping, Linear Advance, accel/jerk tuning, and slicer bed centering polish.

## Confirmed working

- [x] CoreXY jog (correct axes / directions)
- [x] X/Y homing (front-left endstops, normal motor plugs)
- [x] Z / CR Touch homing (`Z_SAFE_HOMING`)
- [x] Manual tram (nozzle at bed screws)
- [x] Auto / probe tram (probe-reachable corners + runtime clamp)
- [x] UBL auto mesh within probe reach (`MESH` ≈ 10–170 × 23–196)
- [x] Measured geometry in overlays (bed/print/probe)
- [x] OrcaSlicer **Duender MGN9H** profile (Custom / Generic Marlin base)
- [x] First sliced smoke test (placement not centered — acceptable for now)

## Not tuned / still open

- [ ] Input Shaping (`M593` / ringing tower)
- [ ] Linear Advance (`M900`)
- [ ] Print / travel accel & jerk beyond conservative defaults
- [ ] Orca bed centering vs physical bed center
- [ ] Multi-machine confirmation of the same geometry

## Validated baseline

| Item | Value |
|------|--------|
| Flash baseline | `0.1.0-beta.3` (see `docs/beta.md`) |
| Motor plugs | Normal X→X, Y→Y |
| Inverts | `INVERT_X_DIR` / `INVERT_Y_DIR` both `true` |
| Steps/mm | X/Y 100, Z 400, E 424.9 |
| Probe XY | `{ -31, -39, 0 }` |
| Bed travel | 0,0 → 201,235 |
| Print area | 1,23 → 200,234 |
| UBL mesh | 10,23 → 170,196 (probe tip reach) |

## Recovery

Keep a known-good `.bin` on a spare SD (e.g. D025 / beta.2 / beta.3). After any flash: `M502` → `M500`, re-set Z offset, re-enable mesh (`M420 S1`).
