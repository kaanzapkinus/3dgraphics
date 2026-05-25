"""
Lesson 3 - Task 1: Change object color
Concept: A material's diffuse color defines the base color of the object
under lighting.

The base scene is a rotating lit cube. In this task we change the diffuse
material color (compare to the original red/cyan example from the slides).
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 1: Try different colors here =====
# RGBA in 0..1 range. Alpha (4th value) = 1.0 means fully opaque.
OBJECT_COLOR = [0.2, 0.6, 1.0, 1.0]   # light blue (was red in the slide example)
# Try also: [1.0, 0.4, 0.1, 1.0] orange, [0.1, 0.9, 0.3, 1.0] green, etc.
# =============================================


def draw_face(nx, ny, nz, v1, v2, v3, v4):
    """Draw one face of the cube with a normal vector (needed for lighting)."""
    glBegin(GL_QUADS)
    glNormal3f(nx, ny, nz)
    glVertex3f(*v1)
    glVertex3f(*v2)
    glVertex3f(*v3)
    glVertex3f(*v4)
    glEnd()


def cube():
    """Unit cube centered at the origin, with proper per-face normals."""
    # Front face (+Z)
    draw_face(0, 0, 1,
              (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5),
              ( 0.5,  0.5,  0.5), (-0.5,  0.5,  0.5))
    # Back face (-Z)
    draw_face(0, 0, -1,
              ( 0.5, -0.5, -0.5), (-0.5, -0.5, -0.5),
              (-0.5,  0.5, -0.5), ( 0.5,  0.5, -0.5))
    # Right face (+X)
    draw_face(1, 0, 0,
              ( 0.5, -0.5,  0.5), ( 0.5, -0.5, -0.5),
              ( 0.5,  0.5, -0.5), ( 0.5,  0.5,  0.5))
    # Left face (-X)
    draw_face(-1, 0, 0,
              (-0.5, -0.5, -0.5), (-0.5, -0.5,  0.5),
              (-0.5,  0.5,  0.5), (-0.5,  0.5, -0.5))
    # Top face (+Y)
    draw_face(0, 1, 0,
              (-0.5,  0.5,  0.5), ( 0.5,  0.5,  0.5),
              ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5))
    # Bottom face (-Y)
    draw_face(0, -1, 0,
              (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5),
              ( 0.5, -0.5,  0.5), (-0.5, -0.5,  0.5))


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 2.0, 3.0, 1.0])


def setup_material():
    # ===== This is what Task 1 changes =====
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, OBJECT_COLOR)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 50.0)


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Lesson 3 - Task 1: Change Object Color", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)
    setup_lighting()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.0)
        glRotatef(glfw.get_time() * 30, 1, 1, 0)

        setup_material()
        cube()

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
