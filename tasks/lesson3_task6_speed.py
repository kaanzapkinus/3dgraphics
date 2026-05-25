"""
Lesson 3 - Task 6: Change animation speed
Concept: Animation in OpenGL is just "redraw the scene every frame and
slightly change a value over time". The rotation speed of the cube is
controlled by a single multiplier applied to glfw.get_time().

Controls:
    UP arrow   -> faster rotation
    DOWN arrow -> slower rotation
    R          -> reset to default speed
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective


# ===== TASK 6: starting speed (degrees per second) =====
DEFAULT_SPEED = 30.0
SPEED_STEP    = 15.0
# =======================================================

current_speed = DEFAULT_SPEED
last_time     = 0.0
current_angle = 0.0


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


def material():
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.4, 0.8, 0.3, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 60.0)


def key_callback(window, key, scancode, action, mods):
    global current_speed
    if action not in (glfw.PRESS, glfw.REPEAT):
        return
    if key == glfw.KEY_UP:
        current_speed += SPEED_STEP
    elif key == glfw.KEY_DOWN:
        current_speed = max(0.0, current_speed - SPEED_STEP)
    elif key == glfw.KEY_R:
        current_speed = DEFAULT_SPEED
    glfw.set_window_title(window, f"Lesson 3 - Task 6: speed = {current_speed:.1f} deg/s  (UP/DOWN/R)")


def main():
    global last_time, current_angle

    if not glfw.init():
        return
    window = glfw.create_window(
        800, 600,
        f"Lesson 3 - Task 6: speed = {DEFAULT_SPEED:.1f} deg/s  (UP/DOWN/R)",
        None, None,
    )
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)
    setup_lighting()

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        # Integrate angle so changing the speed feels smooth (no jumps).
        now = glfw.get_time()
        dt  = now - last_time
        last_time = now
        current_angle = (current_angle + current_speed * dt) % 360.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.0)
        glRotatef(current_angle, 1, 1, 0)

        material()
        cube()

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
