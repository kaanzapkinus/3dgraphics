"""
Lesson 3 - Task 4: Make the cube matte
Concept: A matte surface (like chalk, paper, unglazed clay) scatters light
in all directions equally. It has only DIFFUSE reflection and almost no
SPECULAR component.

To make a cube look matte in OpenGL we:
    - keep the diffuse color
    - set specular color close to black -> [0, 0, 0, 1]
    - set shininess to 0 (or very low)

This file draws TWO cubes for comparison:
    left  = matte cube  (no highlight)
    right = shiny cube  (clear highlight)
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


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


def matte_material():
    """Matte surface: NO specular reflection."""
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.3, 0.3, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 0.0)


def shiny_material():
    """Shiny surface: strong specular highlight."""
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.3, 0.3, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 100.0)


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Lesson 3 - Task 4: Matte (left) vs Shiny (right)", None, None)
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

        # Left cube — matte
        glPushMatrix()
        glTranslatef(-1.0, 0.0, 0.0)
        glRotatef(t, 1, 1, 0)
        matte_material()
        cube()
        glPopMatrix()

        # Right cube — shiny (for comparison)
        glPushMatrix()
        glTranslatef(1.0, 0.0, 0.0)
        glRotatef(t, 1, 1, 0)
        shiny_material()
        cube()
        glPopMatrix()

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
