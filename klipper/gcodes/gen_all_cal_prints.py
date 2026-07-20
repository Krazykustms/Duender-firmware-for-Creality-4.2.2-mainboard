"""Generate Duender calibration print gcodes (geometry only; macros heat/home)."""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "calibrations"
OUT.mkdir(parents=True, exist_ok=True)

LH = 0.20
LW = 0.45
FIL_A = math.pi * (1.75 / 2) ** 2
SPEED = 1800  # mm/min
TRAVEL = 6000
CX, CY = 100.0, 115.0  # bed center-ish


def e_len(mm: float, lh: float = LH, lw: float = LW) -> float:
    return mm * lh * lw / FIL_A


def header(title: str, notes: list[str]) -> list[str]:
    lines = [f"; {title}", "; Macro heats/homes/mesh; this file is motion only"]
    lines.extend(f"; {n}" for n in notes)
    lines += ["G90", "G21", "M83", "G92 E0"]
    return lines


def footer(z_clear: float = 10.0) -> list[str]:
    return [
        "G92 E0",
        "G91",
        "G1 E-2 F1800",
        "G90",
        f"G0 Z{z_clear:.2f} F{TRAVEL}",
        f"G0 X{CX - 40:.3f} Y{CY - 40:.3f} F{TRAVEL}",
        "M104 S0",
        "M140 S0",
        "M84",
        ";END",
    ]


def purge(x: float, y: float) -> list[str]:
    return [
        f"G0 Z{LH:.2f} F{TRAVEL}",
        f"G0 X{x:.3f} Y{y:.3f} F{TRAVEL}",
        f"G1 X{x + 25:.3f} E{e_len(25):.5f} F{SPEED}",
        "G92 E0",
    ]


def square_perimeter(x0: float, y0: float, side: float, z: float) -> list[str]:
    x1, y1 = x0 + side, y0 + side
    path = [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    lines = [f"G0 Z{z:.3f} F{TRAVEL}", f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}"]
    cx, cy = x0, y0
    for nx, ny in path:
        d = math.hypot(nx - cx, ny - cy)
        lines.append(f"G1 X{nx:.3f} Y{ny:.3f} E{e_len(d):.5f} F{SPEED}")
        cx, cy = nx, ny
    return lines


def write(name: str, lines: list[str]) -> Path:
    path = OUT / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {path.name} ({path.stat().st_size} bytes)")
    return path


def gen_pa_tower() -> None:
    side, height = 25.0, 50.0
    x0, y0 = CX - side / 2, CY - side / 2
    layers = int(round(height / LH))
    lines = header(
        "PA tower — single-wall square",
        ["TUNING_TOWER SET_PRESSURE_ADVANCE ADVANCE START=0 FACTOR=0.005", "ADVANCE ≈ height_mm * 0.005"],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        lines.append(f";LAYER:{i} Z={z:.2f} PA~{z * 0.005:.4f}")
        lines += square_perimeter(x0, y0, side, z)
    lines += footer(height + 5)
    write("pa_tower.gcode", lines)


def gen_temp_tower() -> None:
    # 10 mm bands × 5 = 50 mm (macro: START=230 FACTOR=-5 BAND=10 → 230..210)
    side, band_h, bands = 25.0, 10.0, 5
    height = band_h * bands
    x0, y0 = CX - side / 2, CY - side / 2
    layers = int(round(height / LH))
    lines = header(
        "Temp tower — single-wall square",
        ["TUNING_TOWER SET_HEATER_TEMPERATURE TARGET START=230 FACTOR=-5 BAND=10", "Mark best band temp"],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        band = int(z // band_h)
        t_approx = 230 - 5 * band
        lines.append(f";LAYER:{i} Z={z:.2f} TEMP~{t_approx}")
        lines += square_perimeter(x0, y0, side, z)
    lines += footer(height + 5)
    write("temp_tower.gcode", lines)


def gen_retraction_tower() -> None:
    # 5 mm bands, need gaps with travel moves between short pillars — classic is
    # two pillars with travel (retract between). Simplified: square with Z bands
    # + intentional travel off and back each layer for retract.
    side, height = 20.0, 40.0
    x0, y0 = CX - side / 2, CY - side / 2
    x_park, y_park = x0 - 15, y0
    layers = int(round(height / LH))
    lines = header(
        "Retraction tower — wall + hop travel each layer",
        [
            "Requires [firmware_retraction]; TUNING_TOWER SET_RETRACTION RETRACT_LENGTH",
            "START=0.2 FACTOR=0.1 → length ≈ 0.2 + height*0.1",
        ],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        lines.append(f";LAYER:{i} Z={z:.2f} RET~{0.2 + z * 0.1:.2f}")
        lines += square_perimeter(x0, y0, side, z)
        # firmware retraction hops (G10/G11 — requires [firmware_retraction])
        lines += [
            "G10",
            f"G0 Z{z + 0.4:.3f} F{TRAVEL}",
            f"G0 X{x_park:.3f} Y{y_park:.3f} F{TRAVEL}",
            f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}",
            f"G0 Z{z:.3f} F{TRAVEL}",
            "G11",
        ]
    lines += footer(height + 5)
    write("retraction_tower.gcode", lines)


def gen_flow_wall() -> None:
    # Tall single wall 50 mm for flow % measurement (calipers width)
    length, height = 60.0, 50.0
    x0, y0 = CX - length / 2, CY
    layers = int(round(height / LH))
    lines = header(
        "Flow single wall — measure mid-wall width with calipers",
        ["Target width ≈ line width 0.45 mm at 100% flow", "Adjust flow % or rotation_distance"],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        lines.append(f";LAYER:{i} Z={z:.2f}")
        lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
        # alternate direction
        if i % 2 == 0:
            lines.append(f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}")
            lines.append(f"G1 X{x0 + length:.3f} Y{y0:.3f} E{e_len(length):.5f} F{SPEED}")
        else:
            lines.append(f"G0 X{x0 + length:.3f} Y{y0:.3f} F{TRAVEL}")
            lines.append(f"G1 X{x0:.3f} Y{y0:.3f} E{e_len(length):.5f} F{SPEED}")
    lines += footer(height + 5)
    write("flow_wall.gcode", lines)


def gen_first_layer_square() -> None:
    # 40x40 filled first layer squares (3 layers) for bed / Z check
    side = 40.0
    x0, y0 = CX - side / 2, CY - side / 2
    spacing = LW * 0.95
    lines = header(
        "First layer square — bed adhesion / Z offset check",
        ["Look for gaps, elephants foot, shiny/dull; adjust Z offset"],
    )
    lines += purge(x0, y0 - 8)
    for layer in range(3):
        z = LH * (layer + 1)
        lines.append(f";LAYER:{layer} Z={z:.2f}")
        lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
        y = y0
        flip = False
        while y <= y0 + side + 1e-6:
            if not flip:
                lines.append(f"G0 X{x0:.3f} Y{y:.3f} F{TRAVEL}")
                lines.append(f"G1 X{x0 + side:.3f} Y{y:.3f} E{e_len(side):.5f} F{1200}")
            else:
                lines.append(f"G0 X{x0 + side:.3f} Y{y:.3f} F{TRAVEL}")
                lines.append(f"G1 X{x0:.3f} Y{y:.3f} E{e_len(side):.5f} F{1200}")
            flip = not flip
            y += spacing
    lines += footer(10)
    write("first_layer_square.gcode", lines)


def gen_ringing_tower() -> None:
    # Hollow square with fast corner speed for ringing / accel visual
    side, height = 30.0, 60.0
    x0, y0 = CX - side / 2, CY - side / 2
    layers = int(round(height / LH))
    speed_fast = 4800  # 80 mm/s
    lines = header(
        "Ringing tower — fast perimeters for IS / accel visual",
        ["TUNING_TOWER SET_VELOCITY_LIMIT ACCEL START=1000 FACTOR=100 optional", "Or print with Input Shaper disabled first"],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        lines.append(f";LAYER:{i} Z={z:.2f}")
        # override speed for this tower
        x1, y1 = x0 + side, y0 + side
        path = [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
        lines.append(f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}")
        cx, cy = x0, y0
        for nx, ny in path:
            d = math.hypot(nx - cx, ny - cy)
            lines.append(f"G1 X{nx:.3f} Y{ny:.3f} E{e_len(d):.5f} F{speed_fast}")
            cx, cy = nx, ny
    lines += footer(height + 5)
    write("ringing_tower.gcode", lines)


def gen_bridging_test() -> None:
    # Two pillars + bridges at increasing span — simple 30mm gap bridge at Z bands
    # Single 20 mm bridge deck for quick look
    lines = header(
        "Bridge test — short span between walls",
        ["Look for sag; adjust bridge flow/fan/temp in slicer later"],
    )
    # left wall
    xL, xR, y0, length = CX - 20, CX + 20, CY - 10, 20.0
    lines += purge(xL, y0 - 5)
    # build two walls 8 mm tall
    wall_h = 8.0
    for i in range(int(round(wall_h / LH))):
        z = LH * (i + 1)
        lines.append(f";WALL Z={z:.2f}")
        lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
        lines.append(f"G0 X{xL:.3f} Y{y0:.3f} F{TRAVEL}")
        lines.append(f"G1 X{xL:.3f} Y{y0 + length:.3f} E{e_len(length):.5f} F{SPEED}")
        lines.append(f"G0 X{xR:.3f} Y{y0:.3f} F{TRAVEL}")
        lines.append(f"G1 X{xR:.3f} Y{y0 + length:.3f} E{e_len(length):.5f} F{SPEED}")
    # bridge at mid Y across X
    z = wall_h + LH
    mid_y = y0 + length / 2
    span = xR - xL
    lines.append(f";BRIDGE Z={z:.2f}")
    lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
    lines.append(f"G0 X{xL:.3f} Y{mid_y:.3f} F{TRAVEL}")
    lines.append(f"G1 X{xR:.3f} Y{mid_y:.3f} E{e_len(span):.5f} F{900}")
    # second bridge pass
    lines.append(f"G0 Y{mid_y + LW:.3f} F{TRAVEL}")
    lines.append(f"G1 X{xL:.3f} Y{mid_y + LW:.3f} E{e_len(span):.5f} F{900}")
    lines += footer(wall_h + 10)
    write("bridge_test.gcode", lines)


def gen_stringing_test() -> None:
    # Two towers, retract travel between every few layers (classic stringing)
    side, height = 12.0, 40.0
    gap = 30.0
    x0 = CX - gap / 2 - side
    x1 = CX + gap / 2
    y0 = CY - side / 2
    layers = int(round(height / LH))
    lines = header(
        "Filament stringing test — twin towers + G10 travels",
        ["Look for wisps between towers; raise retract / lower temp / dry filament"],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        lines.append(f";LAYER:{i} Z={z:.2f}")
        lines += square_perimeter(x0, y0, side, z)
        lines += ["G10", f"G0 Z{z + 0.6:.3f} F{TRAVEL}", f"G0 X{x1:.3f} Y{y0:.3f} F{TRAVEL}", "G11"]
        lines += square_perimeter(x1, y0, side, z)
        lines += ["G10", f"G0 Z{z + 0.6:.3f} F{TRAVEL}", f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}", "G11"]
    lines += footer(height + 5)
    write("filament_stringing.gcode", lines)


def gen_cooling_tower() -> None:
    # Same as temp wall; fan ramped by TUNING_TOWER M106
    side, height, band = 25.0, 50.0, 10.0
    x0, y0 = CX - side / 2, CY - side / 2
    layers = int(round(height / LH))
    lines = header(
        "Filament cooling / fan tower",
        ["TUNING_TOWER M106 S START=0 FACTOR=51 BAND=10 → 0..255 fan over 50mm", "Overhangs/bridges improve with more fan on PLA"],
    )
    lines += purge(x0, y0 - 5)
    for i in range(layers):
        z = LH * (i + 1)
        fan_approx = min(255, int((z // band) * 51))
        lines.append(f";LAYER:{i} Z={z:.2f} FAN~{fan_approx}")
        lines += square_perimeter(x0, y0, side, z)
    lines += footer(height + 5)
    write("filament_cooling_tower.gcode", lines)


def gen_max_flow() -> None:
    # Thick line segments with increasing feedrate; note when underextrusion starts
    # Speeds 20→60 mm/s in segments at fixed extrusion width (vol flow rises)
    length = 40.0
    x0, y0 = CX - length / 2, CY
    speeds = [1200, 1800, 2400, 3000, 3600, 4200, 4800]  # mm/min
    lines = header(
        "Filament max flow — speed steps on same line path",
        [
            "Vol flow ≈ line_width * layer * speed_mm_s",
            "Note first speed that underextrudes; max ≈ 0.45*0.2*(mm/s) mm³/s",
        ],
    )
    lines += purge(x0, y0 - 5)
    z = LH
    lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
    for i, sp in enumerate(speeds):
        mm_s = sp / 60.0
        vf = LW * LH * mm_s
        lines.append(f";SEG:{i} F={sp} (~{mm_s:.1f}mm/s) ~{vf:.2f} mm3/s")
        # 3 passes at this speed
        for _ in range(3):
            lines.append(f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}")
            lines.append(f"G1 X{x0 + length:.3f} Y{y0:.3f} E{e_len(length):.5f} F{sp}")
            y0 += LW
        y0 = CY
        z += LH
        lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
    lines += footer(15)
    write("filament_max_flow.gcode", lines)


def gen_overhang_test() -> None:
    # Stepped overhangs 10/20/30/40/50 deg approx as increasing cantilever steps
    # Simple: stepped shelfs of increasing stick-out
    lines = header(
        "Filament overhang steps — 2..10 mm stick-out",
        ["Best last clean step; raise fan / lower temp / enable overhangs in slicer"],
    )
    base_w, base_d = 30.0, 20.0
    x0, y0 = CX - base_w / 2, CY - base_d / 2
    lines += purge(x0, y0 - 5)
    # solid base 3 mm
    spacing = LW * 0.95
    for layer in range(15):
        z = LH * (layer + 1)
        lines.append(f";BASE Z={z:.2f}")
        lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
        y = y0
        flip = False
        while y <= y0 + base_d:
            if not flip:
                lines += [f"G0 X{x0:.3f} Y{y:.3f} F{TRAVEL}", f"G1 X{x0 + base_w:.3f} Y{y:.3f} E{e_len(base_w):.5f} F{SPEED}"]
            else:
                lines += [f"G0 X{x0 + base_w:.3f} Y{y:.3f} F{TRAVEL}", f"G1 X{x0:.3f} Y{y:.3f} E{e_len(base_w):.5f} F{SPEED}"]
            flip = not flip
            y += spacing
    # overhang steps: each 2 mm taller, stick out +2 mm in +Y
    z = 3.0
    stick = 0.0
    for step in range(1, 6):
        stick = step * 2.0
        step_h = 2.0
        for i in range(int(round(step_h / LH))):
            z += LH
            y1 = y0 + base_d + stick
            lines.append(f";OVERHANG stick={stick:.0f}mm Z={z:.2f}")
            lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
            # perimeter of extended shelf
            x1 = x0 + base_w
            path = [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
            lines.append(f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}")
            cx, cy = x0, y0
            for nx, ny in path:
                d = math.hypot(nx - cx, ny - cy)
                lines.append(f"G1 X{nx:.3f} Y{ny:.3f} E{e_len(d):.5f} F{1200}")
                cx, cy = nx, ny
            # sparse fill of overhang lip only
            yy = y0 + base_d
            while yy <= y1:
                lines.append(f"G0 X{x0:.3f} Y{yy:.3f} F{TRAVEL}")
                lines.append(f"G1 X{x1:.3f} Y{yy:.3f} E{e_len(base_w):.5f} F{1200}")
                yy += spacing * 2
    lines += footer(z + 8)
    write("filament_overhang.gcode", lines)


def gen_torture_test() -> None:
    """Single print: first-layer bed, walls, overhang, bridge, stringing pillars, fine tip."""
    lines = header(
        "Duender printer torture test — all-in-one quality check",
        [
            "Checks: first layer, vertical walls, overhang, bridge, stringing, fine point",
            "One print ≈ 40×50×35 mm; inspect after cool-down",
        ],
    )
    ox, oy = CX - 20, CY - 25  # origin of part

    def rect_fill(x0, y0, w, d, z, speed=1200):
        sp = LW * 0.92
        chunk = [f"G0 Z{z:.3f} F{TRAVEL}"]
        y, flip = y0, False
        while y <= y0 + d + 1e-9:
            if not flip:
                chunk += [f"G0 X{x0:.3f} Y{y:.3f} F{TRAVEL}", f"G1 X{x0 + w:.3f} Y{y:.3f} E{e_len(w):.5f} F{speed}"]
            else:
                chunk += [f"G0 X{x0 + w:.3f} Y{y:.3f} F{TRAVEL}", f"G1 X{x0:.3f} Y{y:.3f} E{e_len(w):.5f} F{speed}"]
            flip = not flip
            y += sp
        return chunk

    def box_peri(x0, y0, w, d, z, speed=SPEED):
        x1, y1 = x0 + w, y0 + d
        path = [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        chunk = [f"G0 Z{z:.3f} F{TRAVEL}", f"G0 X{x0:.3f} Y{y0:.3f} F{TRAVEL}"]
        cx, cy = x0, y0
        for nx, ny in path:
            dist = math.hypot(nx - cx, ny - cy)
            chunk.append(f"G1 X{nx:.3f} Y{ny:.3f} E{e_len(dist):.5f} F{speed}")
            cx, cy = nx, ny
        return chunk

    lines += purge(ox, oy - 6)

    # --- A: first-layer pad 40×20 ---
    for i in range(2):
        z = LH * (i + 1)
        lines.append(f";FIRST_LAYER Z={z:.2f}")
        lines += rect_fill(ox, oy, 40, 20, z, speed=1000)

    # --- B: hollow walls 20×20 up to Z=15 (dimensional / ringing) ---
    for i in range(int(round(15 / LH))):
        z = 0.4 + LH * (i + 1)
        lines.append(f";WALLS Z={z:.2f}")
        lines += box_peri(ox + 5, oy + 2, 20, 16, z, speed=2400)

    # --- C: overhang steps from right side of pad ---
    z = 15.4
    for stick in (2, 4, 6, 8):
        for _ in range(int(round(2 / LH))):
            z += LH
            lines.append(f";OVERHANG {stick}mm Z={z:.2f}")
            # shelf sticking +Y from wall box
            x0, y0 = ox + 5, oy + 2
            w, d = 20, 16 + stick
            lines += box_peri(x0, y0, w, d, z, speed=1200)

    # --- D: bridge between two stubs ---
    # stubs at top of pad area
    bx0, bx1, by = ox + 2, ox + 38, oy + 22
    bridge_z_base = 2.0
    for i in range(int(round(bridge_z_base / LH))):
        z = LH * (i + 1)
        lines.append(f";BRIDGE_PILLAR Z={z:.2f}")
        lines += box_peri(bx0, by, 4, 4, z)
        lines += box_peri(bx1 - 4, by, 4, 4, z)
    z = bridge_z_base + LH
    span = (bx1 - 4) - (bx0 + 4)
    lines.append(f";BRIDGE Z={z:.2f} span={span:.1f}")
    lines.append(f"G0 Z{z:.3f} F{TRAVEL}")
    lines.append(f"G0 X{bx0 + 4:.3f} Y{by + 2:.3f} F{TRAVEL}")
    lines.append(f"G1 X{bx1 - 4:.3f} Y{by + 2:.3f} E{e_len(span):.5f} F{900}")
    lines.append(f"G0 Y{by + 2 + LW:.3f} F{TRAVEL}")
    lines.append(f"G1 X{bx0 + 4:.3f} Y{by + 2 + LW:.3f} E{e_len(span):.5f} F{900}")

    # --- E: stringing pillars (two thin posts) ---
    px0, px1, py = ox + 8, ox + 28, oy + 28
    for i in range(int(round(20 / LH))):
        z = 2.0 + LH * (i + 1)
        lines.append(f";STRING Z={z:.2f}")
        lines += box_peri(px0, py, 6, 6, z)
        lines += ["G10", f"G0 Z{z + 0.6:.3f} F{TRAVEL}", f"G0 X{px1:.3f} Y{py:.3f} F{TRAVEL}", "G11"]
        lines += box_peri(px1, py, 6, 6, z)
        lines += ["G10", f"G0 Z{z + 0.6:.3f} F{TRAVEL}", f"G0 X{px0:.3f} Y{py:.3f} F{TRAVEL}", "G11"]

    # --- F: fine spike / tip for resolution ---
    sx, sy = ox + 18, oy + 8
    tip_z0 = 15.5
    for i in range(25):
        z = tip_z0 + LH * (i + 1)
        shrink = max(1.2, 6.0 - i * 0.2)
        lines.append(f";TIP Z={z:.2f} s={shrink:.1f}")
        lines += box_peri(sx - shrink / 2, sy - shrink / 2, shrink, shrink, z, speed=900)

    lines += footer(40)
    write("torture_test.gcode", lines)


if __name__ == "__main__":
    gen_pa_tower()
    gen_temp_tower()
    gen_retraction_tower()
    gen_flow_wall()
    gen_first_layer_square()
    gen_ringing_tower()
    gen_bridging_test()
    gen_stringing_test()
    gen_cooling_tower()
    gen_max_flow()
    gen_overhang_test()
    gen_torture_test()
    print("Done:", sorted(p.name for p in OUT.glob("*.gcode")))
