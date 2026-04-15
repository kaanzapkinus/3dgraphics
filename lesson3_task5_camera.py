"""
Lesson 3 - Task 5: Change camera position
Concept: The camera (viewing transformation) decides which side of the
scene the user sees. Moving the camera does NOT move the object — it
just changes the point of view.

Here the cube stays at the origin and the camera is positioned with
gluLookAt(eyeX, eyeY, eyeZ,  centerX, centerY, centerZ,  upX, upY, upZ).
Press 1, 2, 3, 4 to switch between four camera presets.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt


# ===== TASK 5: Camera position presets =====
CAMERAS = {
    "1": dict(name="Front",        eye=(0.0,  0.0,  3.5), up=(0, 1, 0)),
    "2": dict(name="Top-down",     eye=(0.0,  3.5,  0.1), up=(0, 0, -1)),
    "3": dict(name="Side (right)", eye=(3.5,  0.0,  0.0), up=(0, 1, 0)),
    "4": dict(name="Diagonal",     eye=(2.5,  2.0,  2.5), up=(0, 1, 0)),
}
current_camera = "4"
# ===========================================


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
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 3.0, 4.0, 1.0])


def material():
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.3, 0.7, 0.9, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 60.0)


def key_callback(window, key, scancode, action, mods):
    global current_camera
    if action != glfw.PRESS:
        return
    for k in ("1", "2", "3", "4"):
        if key == getattr(glfw, f"KEY_{k}"):
            current_camera = k
            cam = CAMERAS[current_camera]
            glfw.set_window_title(window, f"Lesson 3 - Task 5: Camera = {cam['name']}  (press 1-4)")
            return


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Lesson 3 - Task 5: Camera (press 1-4 to switch)", None, None)
    if not window:
        glfw.terminate(); return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)
    setup_lighting()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60.0, 800.0 / 600.0, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        # ===== Camera (viewing transformation) =====
        cam = CAMERAS[current_camera]
        ex, ey, ez = cam["eye"]
        ux, uy, uz = cam["up"]
        gluLookAt(ex, ey, ez,    # camera position
                  0.0, 0.0, 0.0, # what the camera looks at (origin)
                  ux, uy, uz)    # up direction
        # ============================================

        glRotatef(glfw.get_time() * 20, 0, 1, 0)  # slow rotation to see the cube

        material()
        cube()

        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


main()
