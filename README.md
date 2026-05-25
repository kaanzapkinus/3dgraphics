# 3D Graphics

Coursework for **3D Graphics** at **WSB Merito Wrocław** — Kaan Yazıcıoğlu (SD1, 97364).

The repository is split into two folders:

| Folder | What's inside |
|--------|---------------|
| [`tasks/`](tasks/) | All Lesson 2 / 3 / 4 activities — source code, screenshots and the activity-summary presentation |
| [`final_project/`](final_project/) | The final project (Procedural Solar System, Blender + Python) — the bpy script, the presentation deck, the still render and the 10-second video |

## Lesson activities

All sixteen tasks live in [`tasks/`](tasks/) as standalone Python + OpenGL programs (PyOpenGL + GLFW).

**Lesson 2 — Transformations** (5)
[lesson2_task1_translation.py](tasks/lesson2_task1_translation.py) · [lesson2_task2_scaling.py](tasks/lesson2_task2_scaling.py) · [lesson2_task3_rotation.py](tasks/lesson2_task3_rotation.py) · [lesson2_task4_camera.py](tasks/lesson2_task4_camera.py) · [lesson2_cube.py](tasks/lesson2_cube.py)

**Lesson 3 — Materials, Lighting & Animation** (6)
[lesson3_task1_color.py](tasks/lesson3_task1_color.py) · [lesson3_task2_shininess.py](tasks/lesson3_task2_shininess.py) · [lesson3_task3_light_move.py](tasks/lesson3_task3_light_move.py) · [lesson3_task4_matte.py](tasks/lesson3_task4_matte.py) · [lesson3_task5_camera.py](tasks/lesson3_task5_camera.py) · [lesson3_task6_speed.py](tasks/lesson3_task6_speed.py)

**Lesson 4 — Mesh, Voxel & Analytical** (5)
[lesson4_task1_box.py](tasks/lesson4_task1_box.py) · [lesson4_task2_extraface.py](tasks/lesson4_task2_extraface.py) · [lesson4_task3_voxelres.py](tasks/lesson4_task3_voxelres.py) · [lesson4_task4_voxelcube.py](tasks/lesson4_task4_voxelcube.py) · [lesson4_task5_ellipsoid.py](tasks/lesson4_task5_ellipsoid.py)

The activity-summary deck with screenshots of every task: [`tasks/lessons_tasks.pptx`](tasks/lessons_tasks.pptx) (21 slides).

## Final project — Procedural Solar System

A single Python script run inside Blender that builds the whole scene from scratch:
the Sun, six planets, Saturn's multi-band rings, an asteroid belt, a procedural
star field, animated orbits, lighting and the final render — all via the `bpy` API.

Deliverables in [`final_project/`](final_project/):

| File | Purpose |
|------|---------|
| [solar_system.py](final_project/solar_system.py)   | The bpy script — the project itself |
| [solar_system.pptx](final_project/solar_system.pptx) | Six-slide presentation (video embedded on slide 6) |
| [animation.mp4](final_project/animation.mp4)       | 10-second H.264 video produced by the script |
| [render.png](final_project/render.png)             | Still render at frame 60 |
| [presentation.html](final_project/presentation.html) | Bonus web-based interactive presentation |
| [README.md](final_project/README.md)               | Run instructions for Blender |

A detailed roadmap is also in [FINAL_PROJECT.md](FINAL_PROJECT.md).

## Run

For the lesson activities (Python + OpenGL):

```bash
pip install -r requirements.txt
python tasks/lesson2_task1_translation.py
```

For the final project: open `final_project/solar_system.py` in Blender 4.x or 5.x, switch to the Scripting workspace, and run with **Alt+P**.

## Author

Kaan Yazıcıoğlu — SD1 — 97364
WSB Merito Wrocław
