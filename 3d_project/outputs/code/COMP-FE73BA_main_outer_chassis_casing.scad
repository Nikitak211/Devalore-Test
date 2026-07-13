// Parametric Source File for: main outer chassis casing
// Generated via Sol-5.6-Max-PyOrch CAD Agent
// Component ID: COMP-FE73BA
// Material hint: PLA | Mechanical profile: structural
// Suggested wall_loops from DFM: 4

$fn = 64; // Render resolution
hole_compensation = 0.00; // Dynamic FDM printer gap adjustment

body_w = 60.0;
body_d = 40.0;
body_h = 12.0;
bore_r = 5.0;

module generate_main_outer_chassis_casing_model() {
    difference() {
        // Core structural bounding hull (parametric)
        cube([body_w, body_d, body_h], center = true);

        // Dynamic interlocking peg / clearance track
        translate([0, 0, 0])
            cylinder(h = body_h + 2, r = bore_r + hole_compensation, center = true);
    }
}

generate_main_outer_chassis_casing_model();
