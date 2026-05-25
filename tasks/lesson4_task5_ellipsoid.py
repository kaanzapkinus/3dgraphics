"""
Lesson 4 - Task 5: Modify the analytical sphere equation -> ellipsoid
Concept: Analytical models describe surfaces by equations directly.
A sphere is parameterized by

    x = R * sin(phi) * cos(theta)
    y = R * cos(phi)
    z = R * sin(phi) * sin(theta)

Replacing the single radius R with three different radii Rx, Ry, Rz turns
the sphere into an ellipsoid:

    x = Rx * sin(phi) * cos(theta)
    y = Ry * cos(phi)
    z = Rz * sin(phi) * sin(theta)

The mesh is generated analytically and rendered as quads. Increase
LAT_STEPS and LON_STEPS for a smoother surface.
"""

import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 5: ellipsoid radii (set all three equal to get a sphere) =====
RX, RY, RZ = 1.4, 0.7, 1.0
# =========================================================================

LAT_STEPS = 40   # divisions around the vertical (phi)   axis
LON_STEPS = 60   # divisions around the horizontal (theta) axis


def point_on_ellipsoid(phi, theta, rx=RX, ry=RY, rz=RZ):
    """Analytical surface point. phi in [0, pi], theta in [0, 2*pi]."""
    x = rx * math.sin(phi) * math.cos(theta)
    y = ry * math.cos(phi)
    z = rz * math.sin(phi) * math.sin(theta)
    return x, y, z


def color_for(x, y, z):
    return (0.5 + 0.5 * (x / max(RX, 1e-6)),
            0.5 + 0.5 * (y / max(RY, 1e-6)),
            0.5 + 0.5 * (z / max(RZ, 1e-6)))


def draw_ellipsoid():
    """Tessellate the analytical surface into quads and draw them."""
    for i in range(LAT_STEPS):
        phi1 =       i / LAT_STEPS  * math.pi
        phi2 = (i + 1) / LAT_STEPS  * math.pi
        glBegin(GL_QUAD_STRIP)
        for j in range(LON_STEPS + 1):
            theta = j / LON_STEPS * 2.0 * math.pi
            x1, y1, z1 = point_on_ellipsoid(phi1, theta)
            x2, y2, z2 = point_on_ellipsoid(phi2, theta)
            glColor3f(*color_for(x1, y1, z1))
            glVertex3f(x1, y1, z1)
            glColor3f(*color_for(x2, y2, z2))
            glVertex3f(x2, y2, z2)
        glEnd()


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600,
                                f"Lesson 4 - Task 5: Ellipsoid  Rx={RX} Ry={RY} Rz={RZ}",
                                None, None)
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.1, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(50.0, 800.0 / 600.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.0)
        glRotatef(glfw.get_time() * 30, 0, 1, 0)
        glRotatef(20, 1, 0, 0)

        draw_ellipsoid()

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
