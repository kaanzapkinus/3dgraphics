"""
Lesson 4 - Task 4: Replace spherical condition with cubic -> voxel cube
Concept: The shape of a voxel object is decided entirely by the predicate
"is this cell inside the object?". For a sphere we used
    x^2 + y^2 + z^2 <= r^2
For a cube we instead use a Chebyshev-distance / max-norm condition
    max(|x|, |y|, |z|) <= half_side

So the same grid + voxel generator produces a cube instead of a sphere
just by swapping the condition. Press S/C to switch shapes at runtime
and compare.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


RESOLUTION = 16
HALF_SIDE  = 1.0     # cube fits in [-1, 1]^3
RADIUS     = 1.0     # sphere of radius 1
shape_mode = "cube"  # "cube" or "sphere"


def generate_voxels(predicate, resolution=RESOLUTION, extent=1.0):
    """Sample a regular grid in [-extent, extent]^3 and keep cells where predicate(x,y,z) is True."""
    cells = []
    step = (2.0 * extent) / resolution
    for ix in range(resolution):
        x = -extent + (ix + 0.5) * step
        for iy in range(resolution):
            y = -extent + (iy + 0.5) * step
            for iz in range(resolution):
                z = -extent + (iz + 0.5) * step
                if predicate(x, y, z):
                    cells.append((x, y, z, step))
    return cells


# ===== TASK 4: shape predicates =====
def is_inside_sphere(x, y, z):
    return x * x + y * y + z * z <= RADIUS * RADIUS

def is_inside_cube(x, y, z):
    return max(abs(x), abs(y), abs(z)) <= HALF_SIDE
# =====================================


def draw_cube_cell(cx, cy, cz, size, color):
    s = size / 2.0
    r, g, b = color
    faces = [
        ((-s,-s, s),( s,-s, s),( s, s, s),(-s, s, s)),  # +Z
        (( s,-s,-s),(-s,-s,-s),(-s, s,-s),( s, s,-s)),  # -Z
        (( s,-s, s),( s,-s,-s),( s, s,-s),( s, s, s)),  # +X
        ((-s,-s,-s),(-s,-s, s),(-s, s, s),(-s, s,-s)),  # -X
        ((-s, s, s),( s, s, s),( s, s,-s),(-s, s,-s)),  # +Y
        ((-s,-s,-s),( s,-s,-s),( s,-s, s),(-s,-s, s)),  # -Y
    ]
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glBegin(GL_QUADS)
    for verts in faces:
        glColor3f(r, g, b)
        for v in verts:
            glVertex3f(*v)
    glEnd()
    glPopMatrix()


def color_for(x, y, z):
    # Position-based color so the structure is visible.
    return (0.5 + 0.5 * x, 0.5 + 0.5 * y, 0.5 + 0.5 * z)


def draw_voxels(cells):
    for (x, y, z, size) in cells:
        draw_cube_cell(x, y, z, size, color_for(x, y, z))


_cache = {}
def get_cells(mode):
    if mode not in _cache:
        if mode == "sphere":
            _cache[mode] = generate_voxels(is_inside_sphere)
        else:
            _cache[mode] = generate_voxels(is_inside_cube)
    return _cache[mode]


def key_callback(window, key, scancode, action, mods):
    global shape_mode
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_S:
        shape_mode = "sphere"
    elif key == glfw.KEY_C:
        shape_mode = "cube"
    glfw.set_window_title(window, f"Lesson 4 - Task 4: Voxel {shape_mode}  (press S/C)")


def main():
    if not glfw.init():
        return
    window = glfw.create_window(900, 700,
                                f"Lesson 4 - Task 4: Voxel {shape_mode}  (press S/C)",
                                None, None)
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

        draw_voxels(get_cells(shape_mode))

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
