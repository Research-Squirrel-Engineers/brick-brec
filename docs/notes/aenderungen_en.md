# From the SfM original to the reconstruction: what was changed?

Both models come from KIRI Engine scans (structure from motion). The reconstructions are **not cleaned-up scan meshes**; they are rebuilt procedurally from idealised LEGO bricks. Only dimensions and structure were read from the scans; no mesh and no texture was carried over.

## Common method

- Bricks are cuboids with small chamfers (0.14 mm), a 0.05 mm gap and cylindrical studs (Ø 4.8 mm, 1.7 mm high). Pitch 8 mm, brick height 9.6 mm, everything scaled by 2/3 (scene scale).
- Brick types: 2x4, 2x2, 1x1. Areas are tiled at random (many attempts, best solution by fewest and largest bricks).
- Studs exist only where the next level does not rest on top.
- Materials as colours (PBR, roughness 0.3); export as GLB and OBJ/MTL.

## Model 1: white stepped pyramid with column and minifigure

**Original:** untidy base, noisy edges and studs, the figure on top deformed and stretched.

**Intermediate step:** First only cleaned (levelled, base cut off, heights clamped, Taubin smoothing, holes closed). This was too heavily smoothed for you.

**Reconstruction:**
- 9 levels of 14x18, 12x16, 10x14, 8x12, 6x10, 4x8, 2x6, 2x4, 2x2 studs, with a column of 5 bricks (1x1) on top. All white, only 2x4/2x2/1x1.
- The figure is modelled completely anew from your 11 photos, in minifigure dimensions: helmet with spike and cheek guards, face with moustache, chain-mail print with scarf and belt, tunic, cloak, C-shaped hands, blue legs, brown shoes. Head and torso have painted textures.

**Deviations:** colours of cloak, hands and sleeves slightly paler than in the photo; chain mail as a honeycomb pattern; cheek guards flat; sleeves simple tubes. The hidden brick distribution is random.

## Model 2: stepped pyramid with grey stair arms and temple

**Original:** the mesh has about 69,600 points and 53,500 triangles. The pyramid is rotated by about 16° relative to the ground, the ground is wavy and rises towards the pyramid, the scan is compressed along one axis by about a factor of 0.72, the stair side partly disintegrated, the texture almost colourless.

**Measurement:** alignment by 16.25° (sharpness histogram around the temple centre), height and colour map from 4 million surface points, from which the grid (about 13 cells per stud) and the brick height were derived.

**Reconstruction (version 4):**
- 7 levels. The four grey stair arms are 4 studs wide and reach one stud less far per level (9, 8, 7, 6, 5, 4, 3 studs from the centre).
- White corner areas of 6x6, 5x5, 4x4, 3x3 and, at level 5, 2x2. Above that the corners are free.
- Temple with 4 courses: grey 4x4 course, four white 1x1 corner pillars (hollow in between), grey 4x4 course as lintel, grey 2x2 on top.
- The upper white corner blocks are slightly rotated (2–7° depending on the corner, measured from the scan). The four pillars are rotated by 14°, −12°, 16° and −9°, estimated by eye from your close-up photo.
- Brick count: white 32x 2x4, 20x 2x2, 12x 1x1 and 8 special bricks 1x2/1x4; grey 70x 2x4 and 9x 2x2.

**Assumptions and uncertainties:**
- Seven levels according to the photo and your statement. The scan suggests rather 8 levels with 20x20 studs at the bottom; presumably the lowest levels merge with the table.
- The rotation direction of the pillars and the amount of rotation of the blocks are estimated.
- A few 1x2/1x4 bricks, because odd-sized areas would otherwise need many 1x1 bricks.
- Stair arms at levels 6/7 are not quite symmetrical in the photo but symmetrical in the model. The ground surface of the scan was not carried over.
