"""
Lesson 4 - Task 1: Modify cube mesh -> rectangular box
Concept: A polygon mesh = vertex list + face index list. By changing only
the vertex coordinates (and keeping the same face indices) we change the
shape of the object. Here the symmetric cube becomes a tall, thin box.

Mesh data structure used:
    vertices : list of (x, y, z) points
    faces    : list of (i0, i1, i2) triangle indices into the vertex list
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 1: change these to reshape the box =====
SIZE_X = 0.5
SIZE_Y = 1.5
SIZE_Z = 0.5
# Setting SIZE_X = SIZE_Y = SIZE_Z = 1 gives the original cube.
# ====================================================


def build_box_mesh(sx, sy, sz):
    """Same 8-vertex / 12-triangle index layout as the cube in the slides,
    but vertex coordinates are scaled per axis to make a rectangular box."""
    vertices = [
        (-sx, -sy, -sz), ( sx, -sy, -sz), ( sx,  sy, -sz), (-sx,  sy, -sz),  # back  (z = -)
        (-sx, -sy,  sz), ( sx, -sy,  sz), ( sx,  sy,  sz), (-sx,  sy,  sz),  # front (z = +)
    ]
    faces = [
        (0, 1, 2), (0, 2, 3),  # back
        (4, 6, 5), (4, 7, 6),  # front
        (0, 4, 5), (0, 5, 1),  # bottom
        (3, 2, 6), (3, 6, 7),  # top
        (1, 5, 6), (1, 6, 2),  # right
        (0, 3, 7), (0, 7, 4),  # left
    ]
    # Per-face colors so each side is visible without lighting
    face_colors = [
        (0.9, 0.3, 0.3), (0.9, 0.3, 0.3),
        (0.3, 0.9, 0.3), (0.3, 0.9, 0.3),
        (0.3, 0.5, 0.9), (0.3, 0.5, 0.9),
        (0.9, 0.9, 0.3), (0.9, 0.9, 0.3),
        (0.9, 0.4, 0.9), (0.9, 0.4, 0.9),
        (0.4, 0.9, 0.9), (0.4, 0.9, 0.9),
    ]
    return vertices, faces, face_colors


def draw_mesh(vertices, faces, face_colors):
    glBegin(GL_TRIANGLES)
    for tri, color in zip(faces, face_colors):
        glColor3f(*color)
        for vi in tri:
            glVertex3f(*vertices[vi])
    glEnd()


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600,
                                f"Lesson 4 - Task 1: Box ({SIZE_X} x {SIZE_Y} x {SIZE_Z})",
                                None, None)
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)

    vertices, faces, face_colors = build_box_mesh(SIZE_X, SIZE_Y, SIZE_Z)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        glRotatef(glfw.get_time() * 30, 1, 1, 0)

        draw_mesh(vertices, faces, face_colors)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
