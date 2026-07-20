"""Generate Duender PA tuning tower gcode (geometry only)."""
from pathlib import Path
import math

out = Path(__file__).resolve().parent / "calibrations" / "pa_tower.gcode"
out.parent.mkdir(parents=True, exist_ok=True)

lh = 0.20
lw = 0.45
fil_d = 1.75
fil_a = math.pi * (fil_d / 2) ** 2
speed = 1800
travel = 6000
height = 50.0
side = 25.0
x0, y0 = 90.0, 105.0
x1, y1 = x0 + side, y0 + side


def e_len(mm: float) -> float:
    return mm * lh * lw / fil_a


layers = int(round(height / lh))
lines: list[str] = []
W = lines.append
W("; Duender PA tower — single-wall square")
W("; Pair with TUNING_TOWER SET_PRESSURE_ADVANCE ADVANCE START=0 FACTOR=0.005")
W("; Best band height_mm * 0.005 = pressure_advance; then PA_SAVE")
W("; Macro heats/homes; this file is print motion only")
W("G90")
W("G21")
W("M83")
W("G92 E0")
W(f"G0 Z{lh:.2f} F{travel}")
W(f"G0 X{x0:.3f} Y{y0:.3f} F{travel}")
W(f"G1 X{x0 + 20:.3f} E{e_len(20):.5f} F{speed}")
W("G92 E0")

for i in range(layers):
    z = lh * (i + 1)
    W(f";LAYER:{i} Z={z:.2f} approx_ADVANCE={z * 0.005:.4f}")
    W(f"G0 Z{z:.3f} F{travel}")
    path = [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    cx, cy = x0, y0
    for nx, ny in path:
        dist = math.hypot(nx - cx, ny - cy)
        W(f"G1 X{nx:.3f} Y{ny:.3f} E{e_len(dist):.5f} F{speed}")
        cx, cy = nx, ny

W("G92 E0")
W("G91")
W("G1 E-2 F1800")
W("G90")
W(f"G0 Z{height + 5:.2f} F{travel}")
W(f"G0 X{x0:.3f} Y{y0 - 20:.3f} F{travel}")
W("M104 S0")
W("M140 S0")
W("M84")
W(";END PA tower")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out} layers={layers} bytes={out.stat().st_size}")
