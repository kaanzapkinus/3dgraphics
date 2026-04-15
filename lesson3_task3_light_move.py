"""
Lesson 3 - Task 3: Move the light source
Concept: The position of the light source decides which side of an object
is illuminated and which side is in shadow. By animating the light position
we can clearly see how lighting depends on geometry-light orientation.

The cube stays still here — only the light orbits around it.
The fourth component of GL_POSITION = 1.0 marks this as a point light.
"""

import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 3: Tweak how the light moves =====
LIGHT_ORBIT_RADIUS = 3.0
LIGHT_ORBIT_SPEED  = 1.5   # radians/sec; bigger = faster orbit
LIGHT_HEIGHT       = 1.5
# =============================================


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


def draw_light_marker(x, y, z):
    """Small unlit yellow point so we can SEE where the light currently is."""
    glDisable(GL_LIGHTING)
    glPointSize(12)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.2)
    glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING)


def setup_lighting_static():
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_NORMALIZE)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])


def material():
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.7, 0.7, 0.75, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 60.0)


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Lesson 3 - Task 3: Moving Light Source", None, None)
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.08, 1.0)
    setup_lighting_static()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.0)

        # ===== Animated light position =====
        t = glfw.get_time() * LIGHT_ORBIT_SPEED
        lx = math.cos(t) * LIGHT_ORBIT_RADIUS
        lz = math.sin(t) * LIGHT_ORBIT_RADIUS
        ly = LIGHT_HEIGHT
        # 4th component = 1.0 -> positional (point) light
        glLightfv(GL_LIGHT0, GL_POSITION, [lx, ly, lz, 1.0])
        # ===================================

        material()
        cube()
        draw_light_marker(lx, ly, lz)

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
