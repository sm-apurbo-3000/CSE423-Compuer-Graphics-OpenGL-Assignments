"""Imported Libraries"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math, time




"""Task 1: A House in Rainfall"""
sky_color = [0.0, 0.0, 0.0, 1.0]
angle_shift = 0.0
brightness_change = 0.05
rain_particles = []
fall_speed = 4

class RainParticle:
    def __init__(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y
        self.length = 10  # Length of the raindrop

def draw_rain_line(x, y, tilt_angle):
    glColor3f(65/255, 105/255, 225/255) # blue
    glLineWidth(2)
    glBegin(GL_LINES)
    end_x = x + math.sin(math.radians(tilt_angle)) * 10
    end_y = y - 10
    glVertex2f(x, y)
    glVertex2f(end_x, end_y)
    glEnd()

for _ in range(500):
    rain_particles.append(RainParticle(random.uniform(-100, 600), random.uniform(-100, 600)))

def update_rain_positions():
    global angle_shift, fall_speed
    for particle in rain_particles:
        particle.y -= fall_speed
        particle.x += math.sin(math.radians(angle_shift)) * fall_speed
        if particle.y < 0:
            particle.x = random.uniform(-100, 600)
            particle.y = random.uniform(-100, 600)

def paint_house():
    # House Base
    glColor3f(0.8, 0.4, 0.2)
    glLineWidth(1)
    glBegin(GL_LINES)
    for x in range(120, 381):
        glVertex2f(x, 100)
        glVertex2f(x, 250)
    glEnd()

    # Roof Top
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    # linear interpolation for roof
    for y in range(250, 326):
        left = 100 + (y - 250) * 150 / 75
        right = 400 - (y - 250) * 150 / 75
        glVertex2f(left, y)
        glVertex2f(right, y)
    glEnd()

    # Front Door
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    for x in range(300, 351):
        glVertex2f(x, 100)
        glVertex2f(x, 200)
    glEnd()

    # Door Knob
    glColor3f(1.0, 1.0, 0.0)
    glPointSize(5)
    glBegin(GL_POINTS)
    glVertex2f(340, 150)
    glEnd()

    # Window Panel
    glColor3f(0.7, 0.9, 1.0)
    glBegin(GL_LINES)
    for x in range(150, 201):
        glVertex2f(x, 175)
        glVertex2f(x, 225)
    glEnd()

    # Window Frame
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(175, 225)
    glVertex2f(175, 175)
    glVertex2f(150, 200)
    glVertex2f(200, 200)
    glEnd()

    # Ground Area
    glColor3f(0.0, 0.5, 0.0)
    glLineWidth(1)
    glBegin(GL_LINES)
    for y in range(0, 101):
        glVertex2f(0, y)
        glVertex2f(500, y)
    glEnd()

def handle_arrow_keys(key, x, y):
    global angle_shift
    if key == GLUT_KEY_LEFT:
        angle_shift = max(angle_shift - 2.0, -45.0)
        print("Tilting rain leftward")
    elif key == GLUT_KEY_RIGHT:
        angle_shift = min(angle_shift + 2.0, 45.0)
        print("Tilting rain rightward")
    glutPostRedisplay()

def handle_keyboard_input(key, x, y):
    global sky_color
    if isinstance(key, bytes):
        key = key.decode('utf-8')
    if key == 'd':
        for i in range(3):
            sky_color[i] = min(sky_color[i] + brightness_change, 1.0)
        print("Brightening background")
    elif key == 'n':
        for i in range(3):
            sky_color[i] = max(sky_color[i] - brightness_change, 0.0)
        print("Darkening background")
    glutPostRedisplay()

def animate_scene():
    update_rain_positions()
    glutPostRedisplay()

def setup_scene():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def render_display():
    glClearColor(*sky_color)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_scene()
    paint_house()
    for drop in rain_particles:
        draw_rain_line(drop.x, drop.y, angle_shift)
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(500, 500)
glutInitWindowPosition(0, 0)
glutCreateWindow(b"Task 1: A House in Rainfall")
glutDisplayFunc(render_display)
glutIdleFunc(animate_scene)
glutKeyboardFunc(handle_keyboard_input)
glutSpecialFunc(handle_arrow_keys)
glutMainLoop()




"""Task 2: The Amazing Box"""
# screen_width = 500
# screen_height = 500
# dot_list = [] # list of disctionary of points {x, y, color, speed, dx, dy, blink}
# motion_rate = 0.05
# blink_state = True
# freeze_state = False
# last_blink_time = time.time() # time of last blink toggle

# def render_dot(x_pos, y_pos, color):
#     glPointSize(6)
#     glBegin(GL_POINTS)
#     glColor3f(color[0], color[1], color[2])
#     glVertex2f(x_pos, y_pos)
#     glEnd()

# def generate_dot(x_pos, y_pos):
#     global dot_list, motion_rate
#     color = [random.random(), random.random(), random.random()] # Random color
#     x_shift, y_shift = random.choice([-1, 1]), random.choice([-1, 1])
#     dot_list.append({'x': x_pos, 'y': y_pos, 'color': color, 'speed': motion_rate, 'dx': x_shift, 'dy': y_shift, 'blink': False})

# def invert_coordinate(x_pos, y_pos):
#     global screen_width, screen_height
#     # Invert y-coordinate to match OpenGL's coordinate system
#     return x_pos, (screen_height - y_pos)

# def ClickHandler(button, status, x_pos, y_pos):
#     global dot_list, blink_state
#     if button == GLUT_RIGHT_BUTTON and status == GLUT_DOWN: # if status is down, create a new dot inverted coordinate
#         x_pos, y_pos = invert_coordinate(x_pos, y_pos)
#         print("Creating a new dot at:", x_pos, y_pos)
#         generate_dot(x_pos, y_pos)
        
#     elif button == GLUT_LEFT_BUTTON and status == GLUT_DOWN: # if status is down, toggle blink state of all dots
#         print("Blink toggled.")
#         for dot in dot_list:
#             dot['blink'] = not dot['blink']

# def ArrowHandler(key, x_pos, y_pos):
#     global dot_list, motion_rate
#     if key == GLUT_KEY_UP:
#         print("Incrweasing speed!")
#         motion_rate = min(motion_rate + 0.05, 1)  # Cap speed at 1
#         for dot in dot_list:
#             dot['speed'] = motion_rate
#     elif key == GLUT_KEY_DOWN and motion_rate > 0.05:
#         print("Decreasing speed!")
#         motion_rate = max(motion_rate - 0.05, 0.05)  # Ensure speed doesn't go below 0.05
#         for dot in dot_list:
#             dot['speed'] = motion_rate
#     print("Current speed:", motion_rate)

# def KeyHandler(key, x_pos, y_pos):
#     global freeze_state
#     if key == b' ':
#         freeze_state = not freeze_state
#         print("Freeze toggled.")

# def animate():
#     global dot_list, screen_width, screen_height, freeze_state
#     if not freeze_state:
#         for dot in dot_list:
#             dot['x'] += dot['dx'] * dot['speed']
#             dot['y'] += dot['dy'] * dot['speed']
            
#             # Check for boundary collisions and reverse direction if necessary
#             if dot['x'] >= screen_width or dot['x'] <= 0:
#                 dot['dx'] *= -1
#             if dot['y'] >= screen_height or dot['y'] <= 0:
#                 dot['dy'] *= -1

#     glutPostRedisplay()

# def display():
#     global dot_list, last_blink_time, blink_state
#     glClear(GL_COLOR_BUFFER_BIT)
#     glViewport(0, 0, 500, 500)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
#     glMatrixMode(GL_MODELVIEW)
#     glLoadIdentity()
#     current_time = time.time()

#     if current_time - last_blink_time >= 0.25: # blink every 0.25 seconds
#         blink_state = not blink_state
#         last_blink_time = current_time
    
#     for dot in dot_list:
#         if dot['blink'] and blink_state:
#             render_dot(dot['x'], dot['y'], [0, 0, 0]) # black background color for blink
#         else:
#             render_dot(dot['x'], dot['y'], dot['color'])
#     glutSwapBuffers()

# glutInit()
# glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
# glutInitWindowSize(500, 500)
# glutInitWindowPosition(0, 0)
# box = glutCreateWindow(b"Task 2: The Amazing Box")
# glutDisplayFunc(display)
# glutIdleFunc(animate)
# glutSpecialFunc(ArrowHandler)
# glutMouseFunc(ClickHandler)
# glutKeyboardFunc(KeyHandler)
# glutMainLoop()