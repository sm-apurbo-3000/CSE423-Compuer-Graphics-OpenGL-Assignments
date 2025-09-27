from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, time


"""########## Midpoint Line Algorithm with Zone Conversion Implementation ##########"""


def draw_pixel_point(x, y):
    """Draw a pixel point at the specified coordinates"""
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_midpoint_line(x1, y1, x2, y2):
    """Draw a line using the midpoint algorithm with zone conversion"""
    # converting coordinates to integers
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    # calculating differences
    dx, dy = (x2 - x1), (y2 - y1)
    zone = get_zone(dx, dy)
    
    # converting to Zone 0
    x1_z0, y1_z0 = convert_to_zone0(x1, y1, zone)
    x2_z0, y2_z0 = convert_to_zone0(x2, y2, zone)

    # Midpoint algorithm for zone 0
    dx_z0, dy_z0 = (x2_z0 - x1_z0), (y2_z0 - y1_z0)
    d, y = ((2 * dy_z0) - dx_z0), y1_z0
    delta_E, delta_NE = (2 * dy_z0), (2 * (dy_z0 - dx_z0))

    for x in range(x1_z0, x2_z0 + 1):
        a, b = convert_from_zone0(x, y, zone)
        draw_pixel_point(a, b) # Convert back to original zone and draw point on target pixel
        if d > 0:
            d += delta_NE
            y += 1
        else:
            d += delta_E

def get_zone(dx, dy):
    """Determine the zone of the line segment (0-7) based on the coordinates"""
    if abs(dx) >= abs(dy): # Zone -> 0/3/4/7
        if dx >= 0 and dy >= 0:
            return 0
        elif dx <= 0 and dy >= 0:
            return 3
        elif dx <= 0 and dy <= 0:
            return 4
        else:
            return 7
    else: # Zone -> 1/2/5/6
        if dx >= 0 and dy >= 0:
            return 1
        elif dx <= 0 and dy >= 0:
            return 2
        elif dx <= 0 and dy <= 0:
            return 5
        else:
            return 6

def convert_to_zone0(x, y, zone):
    """Convert coordinates to Zone 0 based on the zone number"""
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    else: # zone == 7
        return x, -y

def convert_from_zone0(x, y, zone):
    """Convert coordinates from Zone 0 to the specified zone"""
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    else: # zone == 7
        return x, -y


"""########## "Catch the Diamonds!" Game Implementation ##########"""


def random_color():
    """Generate a random color with RGB values between 0.5 to 1.0 for the diamond"""
    r, g, b = random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0)
    
    while (r + g + b) / 3 < 0.5:
        r, g, b = random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0)
    
    return (r, g, b)

"""Screen parameters with object size"""
screen_width, screen_height = 600, 800
diamond_size = 15
catcher_width, catcher_height = 100, 20
button_size = 40
fall_speed_init = 1.0
speed_up = 0.005

"""Game state variables"""
game_score, game_over, game_paused = 0, False, False
fall_speed_current = fall_speed_init
last_timestamp = time.time()

"""Game objects dimensions and initial positions"""
diamond_x, diamond_y = random.randint(diamond_size, screen_width - diamond_size), screen_height - diamond_size
diamond_color = random_color()  # Random color for diamond 0.5 ~ 1.0

catcher_x, catcher_y = (screen_width // 2), 5 # Initial position of catcher at the center with fixed height
catcher_color = (1.0, 1.0, 1.0) # Initial color of catcher

def draw_diamond(x, y, size, color):
    """Draw a diamond shape at the specified coordinates"""
    glColor3f(*color)
    draw_midpoint_line(x, y - size, x + size, y)  # bottom to right
    draw_midpoint_line(x + size, y, x, y + size)  # right to top
    draw_midpoint_line(x, y + size, x - size, y)  # top to left
    draw_midpoint_line(x - size, y, x, y - size)  # left to bottom

def draw_catcher(x, y, width, height, color):
    """Draw a catcher shape at the specified coordinates"""
    glColor3f(*color)
    half_width = width // 2
    draw_midpoint_line(x - half_width, y, x + half_width, y)  # bottom line
    draw_midpoint_line(x - half_width, y, x - half_width - 10, y + height)  # left side
    draw_midpoint_line(x + half_width, y, x + half_width + 10, y + height)  # right side
    draw_midpoint_line(x - half_width - 10, y + height, x + half_width + 10, y + height)  # top line

def draw_button(x, y, size, color, symbol, bg_color = (0.0, 0.0, 0.0)):
    """Draw a button at the specified coordinates"""
    # Button's background is square
    glColor3f(*bg_color)
    draw_midpoint_line(x, y, x + size, y)  # bottom line
    draw_midpoint_line(x + size, y, x + size, y + size)  # right side
    draw_midpoint_line(x + size, y + size, x, y + size)  # top line
    draw_midpoint_line(x, y + size, x, y)  # left side

    glColor3f(*color)

    if symbol == "left":
        draw_midpoint_line((x + size // 3), (y + size // 2), (x + 2 * size // 3), (y + size // 4))  # diagonal line
        draw_midpoint_line((x + size // 3), (y + size // 2), (x + 2 * size // 3), (y + 3 * size // 4))  # diagonal line
        draw_midpoint_line((x + size // 3), (y + size // 2), (x + 3 * size // 4), (y + size // 2))  # horizontal line
    elif symbol == "play":
        draw_midpoint_line((x + size // 4), (y + size // 4), (x + size // 4), (y + 3 * size // 4))  # vertical line
        draw_midpoint_line((x + size // 4), (y + size // 4), (x + 3 * size // 4), (y + size // 2))  # diagonal line
        draw_midpoint_line((x + size // 4), (y + 3 * size // 4), (x + 3 * size // 4), (y + size // 2))  # diagonal line
    elif symbol == "pause":
        draw_midpoint_line((x + size // 3), (y + size // 4), (x + size // 3), (y + 3 * size // 4))  # left vertical line
        draw_midpoint_line((x + 2 * size // 3), (y + size // 4), (x + 2 * size // 3), (y + 3 * size // 4))  # right vertical line
    elif symbol == "exit":
        draw_midpoint_line((x + 10), (y + 10), (x + size - 10), (y + size - 10))  # Diagonal line from bottom left to top right
        draw_midpoint_line((x + 10), (y + size - 10), (x + size - 10), (y + 10))  # Diagonal line from top left to bottom right

def has_collided():
    """Check if the diamond has collided with the catcher"""
    diamond_left, diamond_right, diamond_top, diamond_bottom = (diamond_x - diamond_size), (diamond_x + diamond_size), (diamond_y + diamond_size), (diamond_y - diamond_size)
    catcher_left, catcher_right, catcher_top, catcher_bottom = (catcher_x - catcher_width // 2), (catcher_x + catcher_width // 2), (catcher_y + catcher_height), catcher_y
    
    return diamond_left < catcher_right and diamond_right > catcher_left and diamond_bottom < catcher_top and diamond_top > catcher_bottom

def game_reset(x, y):
     """Resets the game state to initial values"""
     global game_score, game_over, game_paused, diamond_x, diamond_y, diamond_color, fall_speed_current, catcher_x, catcher_y, catcher_color

     game_score, game_over, game_paused = 0, False, False
     fall_speed_current = fall_speed_init
     
     diamond_x, diamond_y = random.randint(diamond_size, screen_width - diamond_size), screen_height - diamond_size
     diamond_color = random_color()

     catcher_x, catcher_y = x, y # Previous position of catcher
     catcher_color = (1.0, 1.0, 1.0) # Initial color of catcher

     print("Starting over!")
    
def animate():
    global diamond_x, diamond_y, fall_speed_current, game_score, game_over, last_timestamp, catcher_color, diamond_color
    
    if not game_paused and not game_over:
        current_time = time.time()
        elapsed_time = current_time - last_timestamp
        last_timestamp = current_time
        
        # Update diamond position based on fall speed
        diamond_y -= fall_speed_current * (1 + elapsed_time * 5)  # Speed up over time
        fall_speed_current += speed_up * (elapsed_time * 5)  # Increase fall speed over time
        #print(fall_speed_current)

        # Collision detection
        if diamond_y - diamond_size <= 10 + catcher_height: # Near the catcher height
            if has_collided():
                game_score += 1
                print(f"Score: {game_score}")
                # Reset diamond position and color
                diamond_x, diamond_y = random.randint(diamond_size, screen_width - diamond_size), screen_height - diamond_size
                diamond_color = random_color()
                
            
            elif diamond_y - diamond_size <= 0: # Diamond has fallen below the catcher (MISSED)
                game_over = True
                catcher_color = (1.0, 0.0, 0.0) # RED color for catcher when game over
                print(f"Game Over! Score: {game_score}")
    
    glutPostRedisplay()  # Request a redraw of the window

def keyboard_listener(key, x, y): # Optional for testing purposes
    """Handle keyboard input for game controls"""
    global game_paused, game_score

    if key == b' ' and not game_over:  # Space key to toggle pause
        game_paused = not game_paused
        glutPostRedisplay()  # Request a redraw of the window
    
    elif key == b'\x1b':  # Escape key to exit
        print(f"Goodbye! Final score: {game_score}")
        glutLeaveMainLoop()

def arrow_keys_listener(key, x, y):
    """Handle special keys (e.g., arrow keys) for game controls"""
    global catcher_x

    if not game_over and not game_paused:
        if key == GLUT_KEY_LEFT and (catcher_x - catcher_width // 2 - 10) > 0:
            catcher_x -= 20 # Move catcher left
        elif key == GLUT_KEY_RIGHT and (catcher_x + catcher_width // 2 + 10) < screen_width:
            catcher_x += 20 # Move catcher right
        
        glutPostRedisplay()  # Request a redraw of the window

def mouse_listener(button, state, x, y):
    """Handle mouse input for game controls"""
    global game_over, game_paused, catcher_x, catcher_y

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # convert to OpenGL coordinates for y
        gl_y = screen_height - y

        # check restart button (left)
        if 0 <= x <= (button_size) and (screen_height - button_size) <= gl_y <= (screen_height):
            game_reset(catcher_x, catcher_y)
        
        # check play/pause button (middle)
        elif (screen_width // 2 - button_size // 2) <= x <= (screen_width // 2 + button_size // 2) and (screen_height - button_size) <= gl_y <= (screen_height):
            if not game_over:  # Only toggle pause if the game is not over
                game_paused = not game_paused
        
        # check exit button (right)
        elif (screen_width - button_size) <= x <= (screen_width) and (screen_height - button_size) <= gl_y <= (screen_height):
            print(f"Goodbye! Score: {game_score}")
            glutLeaveMainLoop()  # Exit the main loop

        glutPostRedisplay()  # Request a redraw of the window

def render_game():
    """Render the game"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear the screen
    glLoadIdentity()  # Reset the model-view matrix
    gluOrtho2D(0, screen_width, 0, screen_height)  # Set orthographic projection

    # Draw Reset button
    draw_button(x = 0, y = screen_height - button_size, size = button_size, color = (0.004, 0.976, 0.776), symbol = "left")  # Bright Teal button for reset

    # Draw Play/Pause button
    if game_paused: # Pause state -> draw play button Amber color
        draw_button(x = (screen_width // 2 - button_size // 2), y = (screen_height - button_size), size = button_size, color = (1.0, 0.749, 0.0), symbol = "play")
    else: # Play state -> draw pause button
        draw_button(x = (screen_width // 2 - button_size // 2), y = (screen_height - button_size), size = button_size, color = (1.0, 0.749, 0.0), symbol = "pause")
    
    # Draw Exit button
    draw_button(x = (screen_width - button_size), y = (screen_height - button_size), size = button_size, color = (1.0, 0.0, 0.0), symbol = "exit")  # Red button for exit
    
    if not game_over:
        draw_diamond(diamond_x, diamond_y, diamond_size, diamond_color)  # Draw the diamond
    
    draw_catcher(catcher_x, catcher_y, catcher_width, catcher_height, catcher_color)  # Draw the catcher


    glutSwapBuffers()  # Swap buffers to display the rendered frame




glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)  # Initialize display mode
glutInitWindowSize(screen_width, screen_height)  # Set window size
glutCreateWindow(b"Catch the Diamonds!")  # Create window with title

"""Initialize OpenGL settings"""
glClearColor(0.0, 0.0, 0.0, 1.0)  # Set background color to black
gluOrtho2D(0, screen_width, 0, screen_height)  # Set orthographic projection
glPointSize(2.0)  # Set point size for drawing pixels

glutDisplayFunc(render_game)
glutKeyboardFunc(keyboard_listener)
glutSpecialFunc(arrow_keys_listener)
glutMouseFunc(mouse_listener)
glutIdleFunc(animate)  # Set idle function for animation
glutMainLoop()  # Start main loop of GLUT