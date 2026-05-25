# Final Project — Procedural Solar System

**3D Graphics, WSB Merito Wrocław**
Kaan Yazıcıoğlu — SD1 — 97364

A single Python script that uses Blender's `bpy` API to build a stylised
solar system from nothing — the Sun, six planets, Saturn's multi-band
rings, an asteroid belt, a procedural star field, animated orbits,
lighting, a camera, and the final render. Nothing in the scene is
created by hand in the Blender UI.

## How to run

1. Open **Blender** (4.x recommended; 3.x also supported).
2. Top of the window, switch to the **Scripting** workspace.
3. `File → Open…` and pick `solar_system.py`.
4. (Optional) edit `OUTPUT_DIR_OVERRIDE` at the top of the script if the
   automatic path detection misses the folder.
5. Click **Run Script** (or place the cursor in the editor and press `Alt+P`).

When the script finishes the file shows up next to the script:
* `RENDER_MODE = 'still'`     →  `render.png` (a single PNG, fast)
* `RENDER_MODE = 'animation'` →  `animation.mp4` (10-second H.264 video, several minutes)
* `RENDER_MODE = 'none'`      →  scene only — press **F12** to render manually

Press `SPACE` in the 3D viewport to play the orbits in real time.

## What the script demonstrates

| Course concept | Where in the script |
|----------------|---------------------|
| Transformations & hierarchy (Lesson 2) | Planets parented to orbit-pivot empties, rotation animated on Z |
| Materials & lighting (Lesson 3)        | Emission shader on the Sun, Principled BSDF on planets, single point light at the origin |
| Procedural mesh / programmatic geometry (Lesson 4) | UV-sphere primitives, torus for Saturn's rings, instanced ico-spheres for the asteroid belt — all built from code |
| 3D software + scripting (Lesson 5)     | Entire scene generated through `bpy`, the Blender Python API |

## Configuration

Every scene parameter — planet list, sizes, distances, colours, orbit
periods, camera position, render resolution, animation length — is a
constant at the top of `solar_system.py`. Edit those values and re-run
to get a different solar system.

## Files in this zip

| File | Purpose |
|------|---------|
| `solar_system.py`   | The bpy script — the project itself |
| `solar_system.pptx` | Six-slide presentation describing the project |
| `render.png`        | Still render produced by `RENDER_MODE = 'still'` |
| `animation.mp4`     | 10-second video produced by `RENDER_MODE = 'animation'` (240 frames @ 24 fps) |
| `README.md`         | This file |

## Submission

Per the Moodle upload requirements, the deliverable is a single zip
containing the script, the presentation, the still render, the 10-second
video, and this README.

Final-project requirements met:

* **At least 3 visible 3D objects** — Sun, 6 planets, Saturn's rings,
  asteroid belt instances (10+ objects total).
* **Meaningful background / scene** — procedural star field surrounds
  the whole solar system.
* **Animation** — every planet orbits the Sun and the asteroid belt
  drifts, all keyframed; the included `animation.mp4` is exactly
  10 seconds at 24 fps.
* **Presentation** — `solar_system.pptx`, 6 slides covering the 3D
  objects, how they were built, how the animation was made and how
  the scene was assembled.
