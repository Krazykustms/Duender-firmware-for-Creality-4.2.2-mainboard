// Phase 1 starter: plate that bolts to a standard MGN9H carriage (HIWIN pattern).
// Hole centers: 15 mm (across rail) × 16 mm (along rail). Threads: M3.
// Next: add Sprite gearbox bosses once hole pattern is measured from the STEP.

$fn = 48;

mgn_b = 15;   // across rail
mgn_c = 16;   // along rail
mgn_hole = 3.2; // clearance for M3 screw into carriage
plate_t = 6;
plate_w = 36; // across
plate_l = 50; // along (room for Sprite later)

module mgn9h_holes() {
  for (x = [-mgn_b/2, mgn_b/2], y = [-mgn_c/2, mgn_c/2])
    translate([x, y, -0.1])
      cylinder(d = mgn_hole, h = plate_t + 0.2);
}

difference() {
  // plate: Y = along rail, X = across
  translate([-plate_w/2, -plate_l/2, 0])
    cube([plate_w, plate_l, plate_t]);
  mgn9h_holes();
}

// Visual helpers (not printed) — uncomment to check
// % translate([-10, -19.95, -10]) cube([20, 39.9, 10]); // MGN9H block approx
