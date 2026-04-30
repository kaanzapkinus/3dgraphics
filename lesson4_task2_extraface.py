"""
Lesson 4 - Task 2: Add a new triangular face to the cube
Concept: Mesh connectivity is defined by the face list, not the vertex list.
By adding a NEW vertex (a "tip") and three NEW triangle faces that connect
it to the existing top face, we attach a small pyramid on top of the cube
WITHOUT redefining any existing vertex.

Original cube  = 8 vertices, 12 triangle faces
After this task = 9 vertices, 12 + 4 = 16 triangle faces
    (3 new triangles for the pyramid sides + 1 retained top face base)
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


def build_mesh_with_tip():
    # 8 cube vertices (indices 0..7), exactly as in Lesson 4 slide 13
    vertices = [
        (-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),
        (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),
    ]

    # 12 original cube faces (six sides, two triangles each)
    cube_faces = [
        (0, 1, 2), (0, 2, 3),  # back  (z = -1)
        (4, 6, 5), (4, 7, 6),  # front (z =  1)
        (0, 4, 5), (0, 5, 1),  # bottom
        (3, 2, 6), (3, 6, 7),  # top
        (1, 5, 6), (1, 6, 2),  # right
        (0, 3, 7), (0, 7, 4),  # left
    ]

    # ===== NEW: pyramid tip vertex above the top face =====
    TIP_INDEX = len(vertices)             # = 8
    vertices.append((0.0, 2.0, 0.0))      # tip floats 1 unit above the top

    # ===== NEW: four extra triangle faces connecting tip to the top corners.
    # Top-face vertex indices are: 3 (back-left), 2 (back-right), 6 (front-right), 7 (front-left).
    # CCW winding when seen from outside.
    extra_faces = [
        (3, 2, TIP_INDEX),  # back side of pyramid
        (2, 6, TIP_INDEX),  # right side
        (6, 7, TIP_INDEX),  # front side
        (7, 3, TIP_INDEX),  # left side
    ]
    # ======================================================

    faces = cube_faces + extra_faces

    cube_color  = (0.3, 0.6, 0.9)
    tip_color   = (1.0, 0.5, 0.2)
    face_colors = [cube_color] * len(cube_faces) + [tip_color] * len(extra_faces)

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
    window = glfw.create_window(800, 600, "Lesson 4 - Task 2: Cube + Extra Triangular Faces (Pyramid)",
                                None, None)
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)

    vertices, faces, face_colors = build_mesh_with_tip()
    print(f"Vertices : {len(vertices)}")
    print(f"Faces    : {len(faces)} triangles (12 cube + 4 pyramid)")

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(50.0, 800.0 / 600.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, -0.3, -7.0)
        glRotatef(glfw.get_time() * 30, 0, 1, 0)

        draw_mesh(vertices, faces, face_colors)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
