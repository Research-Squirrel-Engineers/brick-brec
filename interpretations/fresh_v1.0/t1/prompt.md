You are analysing a 3D model with NO prior information. This is a fresh session: you know nothing about the project, the person or the origin of the model. Do not assume a context (toys, archaeology, architecture ...) unless the images or the facts show it.

INPUTS
1. The attached image is a contact sheet with six views of the model (front, right, back, left, top, 3/4). Axes: a and b are the two horizontal axes, "up" is vertical; the front view looks along +b. If photos of the real object are attached as well, treat them as additional evidence (source "photo").
2. FACTS below: objective measurements computed by a script from the mesh. Numbers are reliable; fields described as heuristic can be wrong. The images are authoritative for shape.

TASK
Return ONE JSON document that follows the SCHEMA below, so that others can interpret this model without seeing it.

RULES
1. Output JSON only: no markdown fence, no commentary before or after.
2. Keep observation and interpretation apart: "evidence" = statements that can be checked in the views/facts/photos; "hypotheses" = what the object represents or is made of.
3. Give 2 to 6 hypotheses. Include "free design without a real-world model" or "unknown" if plausible. confidence = your subjective estimate from 0 to 1; hypotheses may overlap and need not sum to 1. Name a specific real-world object only if distinctive evidence supports it; otherwise give a class-level hypothesis and use "specializes" for the specific one. Avoid overconfidence.
4. Every hypothesis must list at least one supporting evidence id; list weakening evidence where it exists. Use ids E1.., H1.., P1.. exactly.
5. Unknown values are null. Do not invent measurements; numbers come from the facts or are explicitly labelled as estimates (with the basis).
6. wikidata_search_term is a plain English search string, never a Q-identifier (you cannot verify identifiers).
7. questions_for_owner: the questions whose answers would settle the most uncertain points.
8. interpreter.model_id_self_reported is your own model identifier as known to you, or "unknown". It is self-reported and may be wrong.
9. Write all text in English. Use the model_id from the facts.

SCHEMA (JSON Schema)
{"$schema":"https://json-schema.org/draft/2020-12/schema","title":"lrec-model-interpretation/1.0","type":"object","required":["schema","model_id","interpreter","object","structure","capture","evidence","hypotheses","questions_for_owner"],"additionalProperties":false,"properties":{"schema":{"const":"lrec-model-interpretation/1.0"},"model_id":{"type":"string","description":"copy from the facts file"},"interpreter":{"type":"object","required":["name","model_id_self_reported","context"],"additionalProperties":false,"properties":{"name":{"type":"string"},"model_id_self_reported":{"type":"string","description":"your model identifier as known to you, or 'unknown'"},"context":{"type":"string","description":"e.g. 'fresh session, no prior knowledge'"}}},"object":{"type":"object","required":["short_description","category","construction_technique","estimated_real_size","up_axis"],"additionalProperties":false,"properties":{"short_description":{"type":"string","maxLength":400},"category":{"enum":["building_or_monument","figurine_or_character","artefact_or_tool","vehicle_or_machine","plant_or_animal","landscape_or_terrain","furniture_or_interior","abstract_or_geometric","scene_or_assembly","unknown"]},"construction_technique":{"enum":["brick_built_toy","carved_or_cut","cast_or_moulded","assembled_from_parts","digital_only","unknown"]},"construction_material":{"type":["string","null"]},"estimated_real_size":{"type":"object","required":["value","unit","confidence"],"additionalProperties":false,"properties":{"value":{"type":["number","null"]},"unit":{"type":["string","null"]},"confidence":{"type":"number","minimum":0,"maximum":1},"basis":{"type":["string","null"]}}},"up_axis":{"type":"object","required":["axis","sign","confidence"],"additionalProperties":false,"properties":{"axis":{"enum":["x","y","z"]},"sign":{"enum":["+","-"]},"confidence":{"type":"number","minimum":0,"maximum":1}}}}},"structure":{"type":"object","required":["overall_shape","levels","symmetry","components","repeated_elements"],"additionalProperties":false,"properties":{"overall_shape":{"type":"string"},"levels":{"type":["integer","null"],"description":"number of stacked levels/steps if clearly visible"},"symmetry":{"type":"object","required":["mirror_axes","rotational_fold"],"additionalProperties":false,"properties":{"mirror_axes":{"type":"array","items":{"enum":["a","b","up"]}},"rotational_fold":{"type":["integer","null"]}}},"components":{"type":"array","items":{"type":"object","required":["id","name","description"],"additionalProperties":false,"properties":{"id":{"type":"string","pattern":"^P[0-9]+$"},"name":{"type":"string"},"description":{"type":"string"},"count":{"type":["integer","null"]}}}},"repeated_elements":{"type":"array","items":{"type":"object","required":["what"],"additionalProperties":false,"properties":{"what":{"type":"string"},"pitch_relative_to_largest_extent":{"type":["number","null"]},"count":{"type":["integer","null"]}}}}}},"capture":{"type":"object","required":["likely_origin","defects","floor_or_background_included"],"additionalProperties":false,"properties":{"likely_origin":{"enum":["photogrammetry","laser_scan","cad_or_procedural","manual_modelling","unknown"]},"defects":{"type":"array","items":{"type":"string"}},"floor_or_background_included":{"type":["boolean","null"]}}},"evidence":{"type":"array","minItems":1,"items":{"type":"object","required":["id","statement","source","strength"],"additionalProperties":false,"properties":{"id":{"type":"string","pattern":"^E[0-9]+$"},"statement":{"type":"string"},"source":{"enum":["views","facts","photo","other"]},"strength":{"enum":["strong","moderate","weak"]}}}},"hypotheses":{"type":"array","minItems":1,"maxItems":8,"items":{"type":"object","required":["id","label","confidence","supports","weakens","alternative_to","specializes","candidate"],"additionalProperties":false,"properties":{"id":{"type":"string","pattern":"^H[0-9]+$"},"label":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1},"supports":{"type":"array","minItems":1,"items":{"type":"string","pattern":"^E[0-9]+$"}},"weakens":{"type":"array","items":{"type":"string","pattern":"^E[0-9]+$"}},"alternative_to":{"type":"array","items":{"type":"string","pattern":"^H[0-9]+$"}},"specializes":{"type":["string","null"],"pattern":"^H[0-9]+$"},"candidate":{"type":"object","required":["label","kind","wikidata_search_term"],"additionalProperties":false,"properties":{"label":{"type":["string","null"]},"kind":{"enum":["type","individual","none"]},"wikidata_search_term":{"type":["string","null"],"description":"plain English search string, never a Q-identifier"}}}}}},"questions_for_owner":{"type":"array","items":{"type":"string"}},"notes":{"type":["string","null"]}}}

FORMAT EXAMPLE (shows only the structure; it is NOT about this model, do not copy content)
{"schema":"lrec-model-interpretation/1.0","model_id":"example_model","interpreter":{"name":"Claude","model_id_self_reported":"unknown","context":"FORMAT EXAMPLE ONLY, not a real analysis"},"object":{"short_description":"Square stepped pyramid with four stair arms and a small roofed shrine on top, built from box-shaped blocks with round studs.","category":"building_or_monument","construction_technique":"brick_built_toy","construction_material":"plastic building bricks","estimated_real_size":{"value":0.1,"unit":"m","confidence":0.3,"basis":"stud pitch relative to bounding box, typical brick pitch 8 mm"},"up_axis":{"axis":"y","sign":"+","confidence":0.9}},"structure":{"overall_shape":"stepped taper with square footprint","levels":7,"symmetry":{"mirror_axes":["a","b"],"rotational_fold":4},"components":[{"id":"P1","name":"stepped body","description":"seven receding levels, light colour at the corners","count":1},{"id":"P2","name":"stair arms","description":"dark strips from base to top on all four sides","count":4},{"id":"P3","name":"shrine","description":"small structure with four corner pillars and a roof on top","count":1}],"repeated_elements":[{"what":"round studs on top faces","pitch_relative_to_largest_extent":0.055,"count":null}]},"capture":{"likely_origin":"cad_or_procedural","defects":["none visible"],"floor_or_background_included":false},"evidence":[{"id":"E1","statement":"Seven receding square levels are visible in all side views.","source":"views","strength":"strong"},{"id":"E2","statement":"Four dark stair arms run from base to top on all four sides.","source":"views","strength":"strong"},{"id":"E3","statement":"The top structure has four corner pillars and a roof.","source":"views","strength":"moderate"},{"id":"E4","statement":"Facts report 7 horizontal surface levels and a periodic stud pattern of about 5 % of the extent.","source":"facts","strength":"moderate"}],"hypotheses":[{"id":"H1","label":"Generic step pyramid with a temple on top","confidence":0.7,"supports":["E1","E2","E3"],"weakens":[],"alternative_to":[],"specializes":null,"candidate":{"label":"step pyramid with temple","kind":"type","wikidata_search_term":"step pyramid"}},{"id":"H2","label":"Free design without a specific real-world model","confidence":0.2,"supports":["E4"],"weakens":[],"alternative_to":["H1"],"specializes":null,"candidate":{"label":null,"kind":"none","wikidata_search_term":null}}],"questions_for_owner":["Is the model based on a real building, and where is it located?"],"notes":"Format example. Hypotheses overlap and need not sum to 1."}

FACTS
{
 "schema": "lrec-model-facts/1.0",
 "model_id": "modelA",
 "file": {
  "name": "modelA.glb",
  "format": "glb",
  "bytes": 3613760
 },
 "counts": {
  "vertices": 128988,
  "vertices_after_merge": 22368,
  "faces": 42996,
  "geometries": 2,
  "connected_components": 435,
  "watertight": true,
  "boundary_edges": 0
 },
 "bounding_box": {
  "min": [
   -0.04795,
   2e-05,
   -0.04795
  ],
  "max": [
   0.04795,
   0.07153,
   0.04795
  ],
  "extents": [
   0.0959,
   0.07151,
   0.0959
  ],
  "diagonal": 0.15332,
  "axes_original": "x,y,z as in file"
 },
 "up_axis_estimate": {
  "axis": "y",
  "sign": "+",
  "method": "glTF specification (Y up)",
  "confidence": 0.9,
  "scores": null
 },
 "units_hint": "metres (glTF specification)",
 "frame_used_for_analysis": "a,b = the two horizontal axes, z = up (derived from up_axis_estimate; views use this frame). Front view looks along +b.",
 "extents_in_analysis_frame": {
  "a": 0.0959,
  "b": 0.0959,
  "up": 0.07151
 },
 "footprint_profile": {
  "slices": 48,
  "plateaus_detected": 10,
  "type": "stepped_taper",
  "base_footprint_ratio": 0.966,
  "top_footprint_ratio": 0.012,
  "note": "plateaus = distinct footprint sizes along the height (robust 0.5-99.5 percentile widths)"
 },
 "horizontal_surface_levels": {
  "count": 10,
  "levels": [
   {
    "height_rel": 0.087,
    "area_share": 0.262
   },
   {
    "height_rel": 0.103,
    "area_share": 0.016
   },
   {
    "height_rel": 0.177,
    "area_share": 0.204
   },
   {
    "height_rel": 0.268,
    "area_share": 0.154
   },
   {
    "height_rel": 0.357,
    "area_share": 0.111
   },
   {
    "height_rel": 0.448,
    "area_share": 0.077
   },
   {
    "height_rel": 0.538,
    "area_share": 0.046
   },
   {
    "height_rel": 0.627,
    "area_share": 0.031
   },
   {
    "height_rel": 0.718,
    "area_share": 0.015
   },
   {
    "height_rel": 0.893,
    "area_share": 0.015
   }
  ],
  "note": "height_rel = 0 base .. 1 top; area_share = share of upward-facing flat area"
 },
 "symmetry": {
  "mirror_a": {
   "permille_of_diagonal": 4.51,
   "rating": "high"
  },
  "mirror_b": {
   "permille_of_diagonal": 4.65,
   "rating": "high"
  },
  "mirror_up": {
   "permille_of_diagonal": 89.3,
   "rating": "low"
  },
  "rot90_about_up": {
   "permille_of_diagonal": 5.14,
   "rating": "medium"
  }
 },
 "periodic_pattern": {
  "detected": true,
  "strength": 0.14,
  "pitch_cells": 14.0,
  "pitch_rel_to_extent_a": 0.0547,
  "note": "heuristic: strongest repeat distance of the top-down height map (relative to bbox, grid 256, high-pass filtered)"
 },
 "appearance": {
  "dominant_colours": [
   {
    "hex": "#303230",
    "share": 0.593
   },
   {
    "hex": "#f5f5f1",
    "share": 0.407
   },
   {
    "hex": "#f5f5f1",
    "share": 0.0
   },
   {
    "hex": "#f5f5f1",
    "share": 0.0
   },
   {
    "hex": "#f5f5f1",
    "share": 0.0
   },
   {
    "hex": "#f5f5f1",
    "share": 0.0
   }
  ],
  "mean_saturation": 0.03,
  "grayscale_like": true,
  "visual_kind": "texture",
  "materials": [
   {
    "visual_kind": "texture",
    "material_name": null
   },
   {
    "visual_kind": "texture",
    "material_name": null
   }
  ]
 },
 "mesh_quality": {
  "edge_length_median": 0.001176,
  "edge_length_p95_over_median": 8.87,
  "degenerate_faces": 0
 },
 "heuristics_note": "Fields marked heuristic are computed by simple rules and can be wrong; the images are authoritative for shape."
}
