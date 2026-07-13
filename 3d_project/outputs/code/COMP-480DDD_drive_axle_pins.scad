// Parametric Source File for: drive axle pins
// Generated via Sol-5.6-Max-PyOrch CAD Agent
// Component ID: COMP-480DDD
// Material hint: PETG | Mechanical profile: load-bearing
// Suggested wall_loops from DFM: 5

$fn = 64; // Render resolution
hole_compensation = 0.15; // Dynamic FDM printer gap adjustment

body_w = 24.0;
body_d = 12.0;
body_h = 8.0;
bore_r = 4.0;

module generate_drive_axle_pins_model() {
    difference() {
        // Core structural bounding hull (parametric)
        cube([body_w, body_d, body_h], center = true);

        // Dynamic interlocking peg / clearance track
        translate([0, 0, 0])
            cylinder(h = body_h + 2, r = bore_r + hole_compensation, center = true);
    }
}

generate_drive_axle_pins_model();
