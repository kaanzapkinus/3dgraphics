"""
Lesson 4 - Task 3: Increase voxel grid resolution -> smoother voxel sphere
Concept: A voxel object samples 3D space on a regular grid. Each cell that
satisfies the sphere condition x^2 + y^2 + z^2 <= r^2 is kept as a small
cube. Higher resolution -> more, smaller cubes -> a smoother-looking sphere.

Press 1, 2, 3, 4 to see the effect of resolution.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 3: try different voxel grid resolutions =====
RESOLUTIONS = {"1": 6, "2": 12, "3": 20, "4": 32}
current_res_key = "2"
# ========================================================

SPHERE_RADIUS = 1.0


def generate_voxel_sphere(resolution, radius=SPHERE_RADIUS):
    """Return a list of (cx, cy, cz, size) cube definitions that approximate a sphere."""
    cells = []
    step = (2.0 * radius) / resolution        # cube edge length
    half = step / 2.0
    r2   = radius * radius
    for ix in range(resolution):
        x = -radius + (ix + 0.5) * step
        for iy in range(resolution):
            y = -radius + (iy + 0.5) * step
            for iz in range(resolution):
                z = -radius + (iz + 0.5) * step
                if x * x + y * y + z * z <= r2:
                    cells.append((x, y, z, step))
    return cells, half


def draw_cube(cx, cy, cz, size):
    s = size / 2.0
    # 6 quads — flat shaded with face color
    faces = [
        # (normal direction, color, four corners)
        ((0, 0,  1), (0.4, 0.7, 1.0), [(-s,-s, s),( s,-s, s),( s, s, s),(-s, s, s)]),
        ((0, 0, -1), (0.2, 0.5, 0.9), [( s,-s,-s),(-s,-s,-s),(-s, s,-s),( s, s,-s)]),
        (( 1, 0, 0), (0.5, 0.8, 1.0), [( s,-s, s),( s,-s,-s),( s, s,-s),( s, s, s)]),
        ((-1, 0, 0), (0.3, 0.6, 0.95),[(-s,-s,-s),(-s,-s, s),(-s, s, s),(-s, s,-s)]),
        ((0,  1, 0), (0.6, 0.85,1.0), [(-s, s, s),( s, s, s),( s, s,-s),(-s, s,-s)]),
        ((0, -1, 0), (0.25,0.5, 0.8), [(-s,-s,-s),( s,-s,-s),( s,-s, s),(-s,-s, s)]),
    ]
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glBegin(GL_QUADS)
    for _, color, verts in faces:
        glColor3f(*color)
        for v in verts:
            glVertex3f(*v)
    glEnd()
    glPopMatrix()


def draw_voxels(cells):
    for (x, y, z, size) in cells:
        draw_cube(x, y, z, size)


def key_callback(window, key, scancode, action, mods):
    global current_res_key
    if action != glfw.PRESS:
        return
    for k in RESOLUTIONS:
        if key == getattr(glfw, f"KEY_{k}"):
            current_res_key = k
            glfw.set_window_title(
                window,
                f"Lesson 4 - Task 3: Voxel sphere  resolution={RESOLUTIONS[k]}^3  (press 1-4)",
            )
            return


_cache = {}
def get_cells(resolution):
    if resolution not in _cache:
        _cache[resolution], _ = generate_voxel_sphere(resolution)
    return _cache[resolution]


def main():
    if not glfw.init():
        return
    window = glfw.create_window(
        900, 700,
        f"Lesson 4 - Task 3: Voxel sphere  resolution={RESOLUTIONS[current_res_key]}^3  (press 1-4)",
        None, None,
    )
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.1, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(45.0, 900.0 / 700.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.5)
        glRotatef(glfw.get_time() * 25, 1, 1, 0)

        draw_voxels(get_cells(RESOLUTIONS[current_res_key]))

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
