"""
Lesson 2 - Hierarchical Cube example
Concept: Build a cube from one face function using glPushMatrix /
glPopMatrix and glRotatef. This is the matrix-stack / hierarchical
modeling pattern from the slides.
"""

import glfw
from OpenGL.GL import *


def square(r, g, b):
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)
    glEnd()


def cube(size):  # Draws a cube with side length = size
    glPushMatrix()  # Save current matrix
    glScalef(size, size, size)  # Scale cube

    square(1, 0, 0)  # red front face

    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    square(0, 1, 0)  # green right face
    glPopMatrix()

    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    square(0, 0, 1)  # blue top face
    glPopMatrix()

    glPushMatrix()
    glRotatef(180, 0, 1, 0)
    square(0, 1, 1)  # cyan back face
    glPopMatrix()

    glPushMatrix()
    glRotatef(-90, 0, 1, 0)
    square(1, 0, 1)  # magenta left face
    glPopMatrix()

    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    square(1, 1, 0)  # yellow bottom face
    glPopMatrix()

    glPopMatrix()  # Restore original matrix


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "OpenGL Cube", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-2, 2, -2, 2, -10, 10)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -2)
        glRotatef(glfw.get_time() * 30, 1, 1, 0)

        cube(1)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()