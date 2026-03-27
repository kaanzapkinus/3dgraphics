"""
Lesson 2 - Task 4: Camera / Viewing Transformation
Concept: Viewing transformation defines where the camera is and what it looks at.

A triangle is drawn at the origin, but the camera orbits around it using
gluLookAt(). This demonstrates how changing the camera position and
viewing direction affects what you see on screen.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluLookAt, gluPerspective
import math


def draw_triangle():
    """Draw a simple colored triangle at the origin."""
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.8, 0.0)   # Yellow vertex (top)
    glVertex3f(0.0, 0.5, 0.0)
    glColor3f(0.0, 0.8, 1.0)   # Cyan vertex (bottom-left)
    glVertex3f(-0.5, -0.5, 0.0)
    glColor3f(1.0, 0.0, 0.8)   # Magenta vertex (bottom-right)
    glVertex3f(0.5, -0.5, 0.0)
    glEnd()


def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Task 4 - Camera / View Transform", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # --- Projection setup (perspective for realistic depth) ---
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)

        # --- Model-View setup ---
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # ===== CAMERA / VIEWING TRANSFORMATION =====
        # The camera orbits around the triangle
        t = glfw.get_time()
        radius = 2.0
        cam_x = math.sin(t * 0.5) * radius   # camera X position orbits
        cam_z = math.cos(t * 0.5) * radius   # camera Z position orbits
        cam_y = 0.5 + math.sin(t * 0.3) * 0.5  # camera bobs up/down slightly

        # gluLookAt(eyeX, eyeY, eyeZ,       -- where the camera IS
        #           centerX, centerY, centerZ -- what the camera LOOKS AT
        #           upX, upY, upZ)            -- which direction is "up"
        gluLookAt(cam_x, cam_y, cam_z,   # eye position (orbiting)
                  0.0, 0.0, 0.0,          # look-at target (origin)
                  0.0, 1.0, 0.0)          # up vector
        # =============================================

        draw_triangle()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


main()
