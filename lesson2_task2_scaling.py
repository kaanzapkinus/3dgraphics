"""
Lesson 2 - Task 2: Scaling
Concept: Scaling changes the size of an object.

A triangle is drawn and its size changes over time using glScalef().
The triangle pulses (grows and shrinks) so you can see scaling in action.
"""

import glfw
from OpenGL.GL import *
import math


def draw_triangle():
    """Draw a simple colored triangle at the origin."""
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.5, 0.0)   # Orange vertex (top)
    glVertex3f(0.0, 0.5, 0.0)
    glColor3f(0.0, 1.0, 0.5)   # Teal vertex (bottom-left)
    glVertex3f(-0.5, -0.5, 0.0)
    glColor3f(0.5, 0.0, 1.0)   # Purple vertex (bottom-right)
    glVertex3f(0.5, -0.5, 0.0)
    glEnd()


def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Task 2 - Scaling", None, None)
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

        # ===== SCALING =====
        # Scale the triangle up and down over time
        t = glfw.get_time()
        scale_factor = 1.0 + 0.8 * math.sin(t * 2.0)  # oscillates between 0.2 and 1.8
        glScalef(scale_factor, scale_factor, 1.0)       # uniform XY scaling
        # ====================

        draw_triangle()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


main()
