# Contributing

Thanks for helping improve Duender firmware configs for the Creality 4.2.2 board.

This repo holds **configuration overlays and docs** — not a fork of Marlin. Upstream firmware lives at [mriscoc/Ender3V2S1](https://github.com/mriscoc/Ender3V2S1).

## Ways to contribute

1. **Measured machine values** — bed size, travel limits, probe offset, verified motor invert flags
2. **Docs fixes** — wiring clarifications, Neo-specific notes, build troubleshooting
3. **CI / tooling** — workflow improvements, reproducible pins for upstream refs
4. **Issue reports** — homing, probing, temperatures, build failures (use the issue templates)

## Before you open a PR

1. Read [docs/wiring.md](docs/wiring.md) and [config/Configuration.h.diff-outline.md](config/Configuration.h.diff-outline.md).
2. If you change `config/features/Duender-CoreXY.json`, confirm either:
   - all `___MEASURE___` placeholders are replaced with real numbers, or
   - `Duender-CoreXY-CI.json` still compiles (CI uses CI defaults).
3. Run a local build (below) or wait for the GitHub Action on your PR.

## Local build

```bash
# Short paths help on Windows
mkdir -p ~/duender-fw && cd ~/duender-fw

git clone https://github.com/mriscoc/Ender3V2S1.git upstream/Ender3V2S1
git -C upstream/Ender3V2S1 checkout New-Year-2025

git clone https://github.com/mriscoc/Special_Configurations.git upstream/Special_Configurations
git -C upstream/Special_Configurations checkout T13

git clone https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard.git duender-config
cd duender-config

# CI-safe defaults (compiles without measured bed size)
bash scripts/ci/generate-config.sh

cd upstream/Ender3V2S1
pio run
```

### Use your measured values locally

```bash
export FEATURE_FILE="$PWD/config/features/Duender-CoreXY.json"
# Edit Duender-CoreXY.json first — no ___MEASURE___ tokens left
bash scripts/ci/generate-config.sh
```

## What to submit for machine profiles

When your Duender is calibrated, a PR updating `Duender-CoreXY.json` (and optionally `Duender-CoreXY-CI.json` if values are widely applicable) is welcome. Include:

| Field | How you measured it |
|-------|---------------------|
| `X_BED_SIZE` / `Y_BED_SIZE` | Usable print area with probe reach |
| `X_MAX_POS` / `Y_MAX_POS` | `M114` at far corner after `G28 X Y` |
| `Z_MAX_POS` | Full Z travel without binding |
| `NOZZLE_TO_PROBE_OFFSET` | Caliper vs nozzle tip, probe pin deployed |
| `INVERT_X_DIR` / `INVERT_Y_DIR` | Note which values worked |

Add a one-line comment in the PR body: toolhead variant, CR Touch mount, Duender PIN version.

## Upstream version policy

CI pins by default:

| Repo | Ref | Why |
|------|-----|-----|
| [Ender3V2S1](https://github.com/mriscoc/Ender3V2S1) | `New-Year-2025` | Current Mriscoc professional branch |
| [Special_Configurations](https://github.com/mriscoc/Special_Configurations) | `T13` | Sprite thermistor + 422 BLT UBL MPC |

Bump these in `.github/workflows/build-firmware.yml` when you validate a newer Mriscoc release. Mention the change in the PR.

## Releases

Firmware binaries are **not** auto-published to GitHub Releases yet. Download build artifacts from the [Actions](https://github.com/Krazykustms/Duender-firmware-for-Creality-4.2.2-mainboard/actions) tab.

Only attach `.bin` files to a Release after you have flashed and smoke-tested them on hardware.

## Code style

- Markdown: clear headings, tables for pin maps, no emojis required
- JSON overlays: valid `CreateConfigs.py` ops (`Enable`, `Disable`, `Custom`, `CustomVal`) — see [mriscoc/Special_Configurations](https://github.com/mriscoc/Special_Configurations)
- Do not commit `.bin` files, EEPROM dumps, or `config/saved-settings/*` with personal meshes

## License

By contributing, you agree your changes are licensed under the same [GPL-3.0](LICENSE) as this repository. Marlin/Mriscoc remain GPL-2.0+.
