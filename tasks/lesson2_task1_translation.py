"""
Lesson 2 - Task 1: Translation
Concept: Translation changes the position of an object in 3D space.

A triangle is drawn and moved to a new position using glTranslatef().
The triangle oscillates left and right so you can see the translation in action.
"""

import glfw
from OpenGL.GL import *
import math


def draw_triangle():
    """Draw a simple colored triangle at the origin."""
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.0, 0.0)   # Red vertex (top)
    glVertex3f(0.0, 0.5, 0.0)
    glColor3f(0.0, 1.0, 0.0)   # Green vertex (bottom-left)
    glVertex3f(-0.5, -0.5, 0.0)
    glColor3f(0.0, 0.0, 1.0)   # Blue vertex (bottom-right)
    glVertex3f(0.5, -0.5, 0.0)
    glEnd()


def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Task 1 - Translation", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glClearColor(0.1, 0.1, 0.15, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)

        # --- Projection setup ---
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-2, 2, -2, 2, -1, 1)

        # --- Model-View setup ---
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # ===== TRANSLATION =====
        # Move the triangle left/right over time using sin()
        t = glfw.get_time()
        tx = math.sin(t) * 1.0   # oscillate on X axis (-1 to +1)
        ty = math.cos(t) * 0.5   # slight vertical movement
        glTranslatef(tx, ty, 0.0)
        # ========================

        draw_triangle()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


main()
