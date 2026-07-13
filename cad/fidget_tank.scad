// Fidget Tank Mechanical Monster — OpenSCAD parametric twin
// Mirrors CadQuery hole-compensation strategy for axle/clip pairs.
// All 13 BOM components selectable via `component_id`.

/* [Global Tolerance] */
printer_hole_compensation = 0.15; // mm — expands female bores
pin_od_nominal = 4.0;
clip_groove_depth = 0.6;

/* [Component Select] */
// "01".."13" matching docs/bom/fidget_tank_bom.json
component_id = "06";

function bore(n) = n + printer_hole_compensation;
function pin_od(n) = n;

module chassis() {
  cube([80, 40, 12], center = true);
  for (x = [-25, 25], y = [-18, 18])
    translate([x, y, 6]) cylinder(h = 8, r = 3);
}

module track_pod() {
  difference() {
    cube([50, 14, 18], center = true);
    for (x = [-15, 0, 15])
      translate([x, 0, 0]) rotate([90, 0, 0])
        cylinder(h = 16, r = bore(pin_od_nominal) / 2, center = true);
  }
}

module road_wheel() {
  difference() {
    cylinder(h = 4, r = 8);
    translate([0, 0, -0.1])
      cylinder(h = 4.2, r = bore(pin_od_nominal) / 2);
  }
}

module axle_c_clip() {
  od = pin_od(pin_od_nominal);
  groove_od = od - 2 * clip_groove_depth;
  difference() {
    cylinder(h = 1.0, r = groove_od / 2 + 1.2);
    translate([0, 0, -0.1]) cylinder(h = 1.2, r = groove_od / 2);
    translate([groove_od / 2 + 1.2, 0, 0.5]) cube([groove_od + 2.4, 1.2, 1.2], center = true);
  }
}

module axle_pin() {
  od = pin_od(pin_od_nominal);
  length = 48;
  difference() {
    cylinder(h = length, r = od / 2);
    translate([0, 0, 3])
      cylinder(h = 1.2, r = od / 2 - clip_groove_depth + 0.01);
    translate([0, 0, length - 4.2])
      cylinder(h = 1.2, r = od / 2 - clip_groove_depth + 0.01);
  }
}

module drive_sprocket() {
  difference() {
    union() {
      cylinder(h = 5, r = 10);
      cylinder(h = 5, r = 12, $fn = 8);
    }
    translate([0, 0, -0.1])
      cylinder(h = 5.2, r = bore(pin_od_nominal) / 2);
  }
}

module track_segment() {
  difference() {
    cube([10, 8, 4], center = true);
    rotate([0, 90, 0])
      cylinder(h = 12, r = 1.0 + printer_hole_compensation * 0.25, center = true);
  }
}

module clicker_leaf() {
  // PETG only — enforced in /config slicing profiles
  cube([30, 8, 1.2], center = true);
}

module turret() { cylinder(h = 10, r = 14); }
module barrel() { cylinder(h = 28, r = 3); }
module hatch_cover() { scale([8, 6, 1]) cylinder(h = 2, r = 1); }

module select_component(id) {
  if (id == "01") chassis();
  else if (id == "02") track_pod();
  else if (id == "03") mirror([1, 0, 0]) track_pod();
  else if (id == "04") road_wheel();
  else if (id == "05") axle_c_clip();
  else if (id == "06") axle_pin();
  else if (id == "07") drive_sprocket();
  else if (id == "08") drive_sprocket();
  else if (id == "09") track_segment();
  else if (id == "10") clicker_leaf();
  else if (id == "11") turret();
  else if (id == "12") barrel();
  else if (id == "13") hatch_cover();
  else assert(false, "Unknown component_id — must be 01..13");
}

select_component(component_id);
