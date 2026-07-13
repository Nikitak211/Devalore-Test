// Parametric Source File for: snap clips
// Generated via Sol-5.6-Max-PyOrch CAD Agent
// Component ID: COMP-BD4146
// Material hint: TPU | Mechanical profile: compliant
// Suggested wall_loops from DFM: 3

$fn = 64; // Render resolution
hole_compensation = 0.25; // Dynamic FDM printer gap adjustment

body_w = 18.0;
body_d = 10.0;
body_h = 4.0;
bore_r = 2.5;

module generate_snap_clips_model() {
    difference() {
        // Core structural bounding hull (parametric)
        cube([body_w, body_d, body_h], center = true);

        // Dynamic interlocking peg / clearance track
        translate([0, 0, 0])
            cylinder(h = body_h + 2, r = bore_r + hole_compensation, center = true);
    }
}

generate_snap_clips_model();
