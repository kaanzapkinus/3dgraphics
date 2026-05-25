"""
Lesson 3 - Task 2: Change shininess
Concept: Shininess controls the size and sharpness of a specular highlight.
- Low shininess  -> wide, dull, blurry highlight
- High shininess -> small, sharp, mirror-like highlight

The base scene is a rotating lit cube. We render TWO cubes side by side so
the effect of shininess is directly visible: left = matte/dull, right = shiny.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 2: Try changing these two shininess values =====
SHININESS_LOW  = 5.0     # dull / wide highlight
SHININESS_HIGH = 120.0   # sharp / focused highlight
# OpenGL allows the range [0, 128]. Try 0 vs 128 for the extreme.
# ===========================================================


def draw_face(nx, ny, nz, v1, v2, v3, v4):
    glBegin(GL_QUADS)
    glNormal3f(nx, ny, nz)
    glVertex3f(*v1); glVertex3f(*v2); glVertex3f(*v3); glVertex3f(*v4)
    glEnd()


def cube():
    draw_face( 0,  0,  1, (-.5,-.5, .5),( .5,-.5, .5),( .5, .5, .5),(-.5, .5, .5))
    draw_face( 0,  0, -1, ( .5,-.5,-.5),(-.5,-.5,-.5),(-.5, .5,-.5),( .5, .5,-.5))
    draw_face( 1,  0,  0, ( .5,-.5, .5),( .5,-.5,-.5),( .5, .5,-.5),( .5, .5, .5))
    draw_face(-1,  0,  0, (-.5,-.5,-.5),(-.5,-.5, .5),(-.5, .5, .5),(-.5, .5,-.5))
    draw_face( 0,  1,  0, (-.5, .5, .5),( .5, .5, .5),( .5, .5,-.5),(-.5, .5,-.5))
    draw_face( 0, -1,  0, (-.5,-.5,-.5),( .5,-.5,-.5),( .5,-.5, .5),(-.5,-.5, .5))


def setup_lighting():
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_NORMALIZE)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 2.0, 3.0, 1.0])


def material(diffuse, shininess):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, shininess)


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Lesson 3 - Task 2: Shininess (left=dull, right=shiny)", None, None)
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)
    setup_lighting()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.0)

        t = glfw.get_time() * 30

        # Left cube — low shininess (dull, matte-like highlight)
        glPushMatrix()
        glTranslatef(-1.0, 0.0, 0.0)
        glRotatef(t, 1, 1, 0)
        material([0.2, 0.6, 1.0, 1.0], SHININESS_LOW)
        cube()
        glPopMatrix()

        # Right cube — high shininess (small, sharp highlight)
        glPushMatrix()
        glTranslatef(1.0, 0.0, 0.0)
        glRotatef(t, 1, 1, 0)
        material([0.2, 0.6, 1.0, 1.0], SHININESS_HIGH)
        cube()
        glPopMatrix()

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
