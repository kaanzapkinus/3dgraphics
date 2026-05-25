"""
Lesson 2 - Task 3: Rotation
Concept: Rotation in 3D is always about an axis.

A triangle is drawn and continuously rotated around the Z axis using glRotatef().
You can see the triangle spinning in place.
"""

import glfw
from OpenGL.GL import *


def draw_triangle():
    """Draw a simple colored triangle at the origin."""
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.2, 0.2)   # Red vertex (top)
    glVertex3f(0.0, 0.5, 0.0)
    glColor3f(0.2, 1.0, 0.2)   # Green vertex (bottom-left)
    glVertex3f(-0.5, -0.5, 0.0)
    glColor3f(0.2, 0.2, 1.0)   # Blue vertex (bottom-right)
    glVertex3f(0.5, -0.5, 0.0)
    glEnd()


def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Task 3 - Rotation", None, None)
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

        # ===== ROTATION =====
        # Rotate the triangle around the Z axis (the axis pointing at you)
        angle = glfw.get_time() * 60.0  # 60 degrees per second
        glRotatef(angle, 0.0, 0.0, 1.0)  # rotate around Z axis
        # =====================

        draw_triangle()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


main()
