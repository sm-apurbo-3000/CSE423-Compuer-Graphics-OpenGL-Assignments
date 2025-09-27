from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random
from ThreeD_OpenGL_Intro import draw_text

# Camera-related variables
camera_pos = (0,500,500)
# Camera control variables
camera_angle = 0  # Angle around the arena (degrees)
camera_height = 500  # Height (z)
camera_radius = 500  # Distance from center
camera_mode = 'third'  # 'third' or 'first'

fovY = 90  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423

# Player position and rotation variables
player_x = 0
player_y = 0
player_angle = 0  # In degrees
MOVE_SPEED = 5.0  
ROTATION_SPEED = 5.0  # Constant rotation speed

# Enemy data: list of dicts with x, y positions
num_enemies = 5
enemy_radius = 25  
player_radius = 15
enemies = [] # [{'x':_, 'y':_}, {'x':_, 'y':_}, ...]

# Bullet system variables
bullets = []  # List to store active bullets' obj
BULLET_SPEED = 15
BULLET_LIFETIME = 100  # Number of frames a bullet lives for
BULLET_RADIUS = 5

# Key state tracking
keys_pressed = {'w': False, 's': False, 'a': False, 'd': False}

# Cheat mode and auto-follow state
cheat_mode = False
auto_follow = False
cheat_fire_cooldown = 0  # To control auto-fire rate

# Game state variables
player_life = 5
game_score = 0
bullets_missed = 0
game_over = False
player_hit_cooldown = 0 # to control hit cooldown min time interval between teo hits
fall_angle = 0  # Angle for falling animation

# Enemy animation variables
ENEMY_PULSE_SPEED = 0.5  # Speed of size pulsing
enemy_base_size = enemy_radius  # Store the base size for pulsing calculation

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.lifetime = BULLET_LIFETIME
        # Calculate velocity based on angle
        rad = math.radians(angle)
        self.dx = BULLET_SPEED * math.cos(rad)
        self.dy = BULLET_SPEED * math.sin(rad)
    
    def check_enemy_collision(self):
        global enemies, game_score
        current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        
        for enemy in enemies:
            dx = self.x - enemy['x']
            dy = self.y - enemy['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Use current pulsing size for collision
            pulse_factor = 1.0 + 0.2 * math.sin(current_time * ENEMY_PULSE_SPEED * 2 * math.pi)
            current_radius = enemy_base_size * pulse_factor
            
            if dist < current_radius + BULLET_RADIUS:
                # Respawn enemy at a new location
                new_pos = spawn_enemy()
                enemy['x'] = new_pos['x']
                enemy['y'] = new_pos['y']
                game_score += 1
                return True
        return False

def spawn_enemy():
    tile_size = 40
    num_tiles = 30
    margin = 60
    arena_min = -tile_size * num_tiles // 2 + margin
    arena_max = tile_size * num_tiles // 2 - margin
    x = random.randint(arena_min, arena_max)
    y = random.randint(arena_min, arena_max)
    return {'x': x, 'y': y}

def reset_enemies():
    global enemies
    enemies = [spawn_enemy() for _ in range(num_enemies)]

reset_enemies() # initial enemy generation

def draw_player():
    glPushMatrix()
    
    if camera_mode == 'first' and not game_over:
        # Draw arms and gun for first-person view
        glTranslatef(player_x, player_y, 40)  # Position at camera height
        glRotatef(player_angle, 0, 0, 1)  # Rotate with player view
        
        # Draw arms (smaller and positioned lower for FPS view)
        glColor3f(0.96, 0.8, 0.69)  
        
        # Left arm
        glPushMatrix()
        glTranslatef(0, 15, -15) # (x=y, y=x, z)    
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 10, 2, 40, 24, 24)
        glPopMatrix()

        # Left arm
        glPushMatrix()
        glTranslatef(0, -15, -15) # (x=y, y=x, z)    
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 10, 2, 40, 24, 24)
        glPopMatrix()

        # Draw gun (positioned between arms)
        glColor3f(0.5, 0.5, 0.5)  # Gray
        glPushMatrix()
        glTranslatef(0, 0, -15)  
        glRotatef(90, 0, 1, 0)  
        gluCylinder(gluNewQuadric(), 8, 4, 60, 24, 24) 
        glPopMatrix()
        
    else:
        # Regular third-person view drawing
        glTranslatef(player_x, player_y, 0)
        glRotatef(-90, 0, 0, 1)
        glRotatef(player_angle, 0, 0, 1)
        
        if game_over:
            # Fall (around X axis)
            glRotatef(fall_angle, 1, 0, 0)
        
        glScalef(1.0, 1.0, 1.0)

        ## --- BODY (Main Block) ---
        glColor3f(0.0, 0.5, 0.0)
        glPushMatrix()
        glScalef(1.0, 1.0, 2.0)
        glutSolidCube(30)
        glPopMatrix()

        ## --- GUN ---
        glColor3f(0.5, 0.5, 0.5)  
        glPushMatrix()
        glTranslatef(0, 10, 10)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 5, 60, 24, 24)
        glRotatef(180, 1, 0, 0)
        glPopMatrix()

        ## --- LEGS ---
        glColor3f(0.0, 0.0, 1.0)
        glPushMatrix()
        glTranslatef(-10, 0, -25)
        glScalef(0.4, 0.4, 1.0)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 20, 10, 30, 24, 24)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(10, 0, -25)
        glScalef(0.4, 0.4, 1.0)
        glRotatef(180, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 20, 10, 30, 24, 24)
        glPopMatrix()

        ## --- HEAD ---
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glutSolidSphere(12, 20, 20)
        glPopMatrix()

        ## --- ARMS ---
        glColor3f(0.96, 0.8, 0.69)
        glPushMatrix()
        glTranslatef(-15, 10, 10)
        glScalef(0.4, 1.2, 0.4)
        glRotatef(270, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 8, 15, 24, 24)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(15, 10, 10)
        glScalef(0.4, 1.2, 0.4)
        glRotatef(270, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 8, 15, 24, 24)
        glPopMatrix()

    glPopMatrix()

def keyboardListener(key, x, y):
    global keys_pressed, cheat_mode, auto_follow, game_over
    if key == b'r' and game_over:
        reset_game()
    if not game_over:  # Only process movement keys if game is not over
        if key == b'w':
            keys_pressed['w'] = True
        elif key == b's':
            keys_pressed['s'] = True
        elif key == b'a':
            keys_pressed['a'] = True
        elif key == b'd':
            keys_pressed['d'] = True
        elif key == b'c':
            cheat_mode = not cheat_mode
        elif key == b'v':
            auto_follow = not auto_follow

def keyboardUpListener(key, x, y):
    global keys_pressed
    if key == b'w':
        keys_pressed['w'] = False
    elif key == b's':
        keys_pressed['s'] = False
    elif key == b'a':
        keys_pressed['a'] = False
    elif key == b'd':
        keys_pressed['d'] = False

def update_player_movement():
    global player_x, player_y, player_angle
    
    # Get movement direction based on player's angle
    rad = math.radians(player_angle)
    forward_x = math.cos(rad)
    forward_y = math.sin(rad)
    
    # Apply constant speed movement based on key states
    if keys_pressed['w']:
        player_x += forward_x * MOVE_SPEED
        player_y += forward_y * MOVE_SPEED
    if keys_pressed['s']:
        player_x -= forward_x * MOVE_SPEED
        player_y -= forward_y * MOVE_SPEED
    if not cheat_mode:  # Only allow manual rotation when not in cheat mode
        if keys_pressed['a']:
            player_angle += ROTATION_SPEED
        if keys_pressed['d']:
            player_angle -= ROTATION_SPEED
    
    # Arena boundaries
    tile_size = 40
    num_tiles = 30
    margin = 40
    arena_min = -tile_size * num_tiles // 2 + margin
    arena_max = tile_size * num_tiles // 2 - margin

    # Clamp position to arena boundaries
    player_x = max(arena_min, min(arena_max, player_x))
    player_y = max(arena_min, min(arena_max, player_y))

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_angle, camera_height, camera_mode
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_height = min(1000, camera_height + 20)
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_height = max(50, camera_height - 20)
    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5


def mouseListener(button, state, x, y):
    global bullets, player_x, player_y, player_angle, camera_mode
    
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Create new bullet at player's position with player's angle
        new_bullet = Bullet(player_x, player_y, player_angle)
        bullets.append(new_bullet)
        print("Player Bullet Fired!")
    
    # Right mouse button toggles camera mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == 'third':
            camera_mode = 'first'
        else:
            camera_mode = 'third'


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)  # Reduced FOV for first person
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    global camera_angle, camera_height, camera_radius, camera_mode, player_x, player_y, player_angle, cheat_mode, auto_follow
    if camera_mode == 'third':
        # Third-person: orbit around center
        rad = math.radians(camera_angle)
        x = camera_radius * math.cos(rad)
        y = camera_radius * math.sin(rad)
        z = camera_height
        gluLookAt(x, y, z,
                  0, 0, 0,
                  0, 0, 1)
    else:
        # First-person: position at player's eye level
        rad = math.radians(player_angle)
        px = player_x
        py = player_y
        pz = 45  # Lower camera height for better perspective
        
        # Look ahead in the direction player is facing
        look_x = px + math.cos(rad)
        look_y = py + math.sin(rad)
        look_z = 45  # Keep look direction level
        
        #If cheat mode and auto-follow are active, adjust look direction to nearest enemy
        if cheat_mode and auto_follow:
            enemy, angle_to_enemy = is_enemy_in_line_of_sight()
            if enemy:
                rad = math.radians(angle_to_enemy)
                look_x = px + math.cos(rad)
                look_y = py + math.sin(rad)
        
        elif cheat_mode and not auto_follow:
            look_x = px
            look_y = py + 15

        gluLookAt(px, py, pz,
                  look_x, look_y, look_z,
                  0, 0, 1)

def draw_enemies():
    global enemies, game_over
    if game_over:
        return  # Don't draw enemies when game is over
    
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0  # Get time in seconds
    
    for enemy in enemies:
        glPushMatrix()
        dx = player_x - enemy['x']
        dy = player_y - enemy['y']
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 1:
            pulse_speed = ENEMY_PULSE_SPEED * 2.2
        else:
            pulse_speed = ENEMY_PULSE_SPEED * 0.7
        pulse_factor = 1.0 + 0.2 * math.sin(current_time * pulse_speed * 2 * math.pi)
        current_radius = enemy_base_size * pulse_factor
        
        glTranslatef(enemy['x'], enemy['y'], current_radius)
        glColor3f(1.0, 0.0, 0.0)  # Red body
        glutSolidSphere(current_radius, 20, 20)
        
        glTranslatef(0, 0, current_radius + 12 * pulse_factor)
        glColor3f(0.0, 0.0, 0.0)  # Black head
        glutSolidSphere(12 * pulse_factor, 20, 20)
        glPopMatrix()


def update_enemies():
    global enemies, player_x, player_y, player_life, game_over, player_hit_cooldown
    if game_over:
        return
        
    move_speed = 1
    tile_size = 40
    num_tiles = 30
    margin = 40
    arena_min = -tile_size * num_tiles // 2 + margin
    arena_max = tile_size * num_tiles // 2 - margin

    for enemy in enemies:
        dx = player_x - enemy['x']
        dy = player_y - enemy['y']
        dist = math.sqrt(dx*dx + dy*dy)
        # Move towards player if not too close
        if dist > 1:
            enemy['x'] += move_speed * dx / dist
            enemy['y'] += move_speed * dy / dist

        # Clamp enemies inside boundaries
        enemy['x'] = max(arena_min, min(arena_max, enemy['x']))
        enemy['y'] = max(arena_min, min(arena_max, enemy['y']))

        # Check collision with player (using current pulsing size)
        current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        if dist > 1:
            pulse_speed = ENEMY_PULSE_SPEED * 2.2
        else:
            pulse_speed = ENEMY_PULSE_SPEED * 0.7
        pulse_factor = 1.0 + 0.2 * math.sin(current_time * pulse_speed * 2 * math.pi)
        current_radius = enemy_base_size * pulse_factor
        if dist < current_radius + player_radius and player_hit_cooldown <= 0:
            player_life -= 1
            print(f"Remaining Player Life: {player_life}")
            player_hit_cooldown = 30 # player got hit
            if player_life <= 0:
                game_over = True
                enemies.clear()
                bullets.clear()
            # Respawn enemy
            new_pos = spawn_enemy()
            enemy['x'] = new_pos['x']
            enemy['y'] = new_pos['y']

def is_enemy_in_line_of_sight():
    # Returns (enemy, angle_to_enemy) if any enemy is in line of sight, else (None, None)
    min_dist = float('inf')
    target_enemy = None
    target_angle = None
    for enemy in enemies:
        dx = enemy['x'] - player_x
        dy = enemy['y'] - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        angle_to_enemy = math.degrees(math.atan2(dy, dx))
        angle_diff = (angle_to_enemy - player_angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360
        # Consider in line of sight if within 5 degrees
        if abs(angle_diff) < 5 and dist < min_dist:
            min_dist = dist
            target_enemy = enemy
            target_angle = angle_to_enemy
    if target_enemy:
        return target_enemy, target_angle
    return None, None

def reset_game():
    global player_life, game_score, bullets_missed, game_over
    global player_x, player_y, player_angle
    global cheat_mode, auto_follow, cheat_fire_cooldown
    global fall_angle
    player_life = 5
    game_score = 0
    bullets_missed = 0
    game_over = False
    player_x = 0
    player_y = 0
    player_angle = 0
    cheat_mode = False
    auto_follow = False
    cheat_fire_cooldown = 0
    fall_angle = 0
    reset_enemies()

def idle():
    global player_hit_cooldown, player_angle, cheat_mode, cheat_fire_cooldown, fall_angle
    if not game_over:
        update_player_movement()
        update_enemies()
        update_bullets()
        if player_hit_cooldown > 0:
            player_hit_cooldown -= 1
        # Cheat mode logic
        if cheat_mode:
            player_angle = (player_angle + 4) % 360
            enemy, angle_to_enemy = is_enemy_in_line_of_sight()
            if enemy and cheat_fire_cooldown <= 0:
                new_bullet = Bullet(player_x, player_y, player_angle)
                bullets.append(new_bullet)
                cheat_fire_cooldown = 5 # shot fired!
                print("Player Bullet Fired!")
            if cheat_fire_cooldown > 0:
                cheat_fire_cooldown -= 1
    else:
        # Animate fall angle up to 90 degrees
        if fall_angle < 90:
            fall_angle += 3  # Slightly slower fall for more dramatic effect
            if fall_angle > 90:
                fall_angle = 90
    glutPostRedisplay()

def draw_boundaries():
    """
    Draws the colored boundary walls around the arena
    """
    tile_size = 40
    num_tiles = 30
    arena_size = tile_size * num_tiles
    wall_height = 100  # Height of the walls
    start = -arena_size // 2
    end = arena_size // 2

    # Draw the walls
    glBegin(GL_QUADS)
    
    # Left wall (Blue)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(start, start, 0)
    glVertex3f(end, start, 0)
    glVertex3f(end, start, wall_height)
    glVertex3f(start, start, wall_height)
    
    # Near wall (White)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(end, start, 0)
    glVertex3f(end, end, 0)
    glVertex3f(end, end, wall_height)
    glVertex3f(end, start, wall_height)
    
    # Right wall (Green)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(end, end, 0)
    glVertex3f(start, end, 0)
    glVertex3f(start, end, wall_height)
    glVertex3f(end, end, wall_height)
    
    # Far wall (Cyan)
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(start, end, 0)
    glVertex3f(start, start, 0)
    glVertex3f(start, start, wall_height)
    glVertex3f(start, end, wall_height)
    
    glEnd()

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw the chessboard arena
    tile_size = 40
    num_tiles = 30  # 30x30 tiles for a large arena
    start = -tile_size * num_tiles // 2
    
    for i in range(num_tiles):
        for j in range(num_tiles):
            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)  # White
            else:
                glColor3f(0.7, 0.4, 0.9)  # Purple
            x = start + i * tile_size
            y = start + j * tile_size
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
            glEnd()

    # Draw the boundary walls
    draw_boundaries()
    
    draw_enemies()
    draw_player()
    draw_bullets()
    
    # Draw HUD
    if not game_over:
        draw_text(10, 770, f"Player Life Remaining: {player_life}")
        draw_text(10, 740, f"Game Score: {game_score}")
        draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")
    
    else:
        draw_text(10, 770, f"Game is Over. Your Score is {game_score}.")
        draw_text(10, 740, f"Press \"R\" to RESTART the Game.")
    
    glutSwapBuffers()

def draw_bullets():
    if game_over:
        return
    else:
        glColor3f(1.0, 0.0, 0.0)  # Red bullets
        for bullet in bullets:
            glPushMatrix()
            glTranslatef(bullet.x, bullet.y, 30)  # Same height as player's gun
            glRotatef(bullet.angle, 0, 0, 1)  # Rotate bullet to match shooting direction
            glScalef(BULLET_RADIUS * 0.2, BULLET_RADIUS * 0.2, BULLET_RADIUS * 0.2)
            glutSolidCube(BULLET_RADIUS * 2)  # Cube bulle
            glPopMatrix()

def update_bullets():
    global bullets, bullets_missed, game_over
    # Arena boundaries
    tile_size = 40
    num_tiles = 30
    margin = 0  # Bullets can go right up to the edge
    arena_min = -tile_size * num_tiles // 2 + margin
    arena_max = tile_size * num_tiles // 2 - margin

    new_bullets = []
    for bullet in bullets:
        # Update bullet position
        bullet.x += bullet.dx
        bullet.y += bullet.dy
        bullet.lifetime -= 1
        
        # Check if bullet is out of bounds or expired
        if (bullet.x < arena_min or bullet.x > arena_max or 
            bullet.y < arena_min or bullet.y > arena_max or 
            bullet.lifetime <= 0):
            bullets_missed += 1
            print(f"Bullet missed: {bullets_missed}")
            if bullets_missed >= 10:
                game_over = True
                enemies.clear()
                bullets.clear()
            continue
            
        # Check for enemy collision
        if bullet.check_enemy_collision():
            continue
            
        # Keep bullet if it's still valid
        new_bullets.append(bullet)
    
    bullets = new_bullets

# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    glutCreateWindow(b"Bullet Frenzy - A 3D Game with Player Movement, Shooting, & Cheat Modes")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutKeyboardUpFunc(keyboardUpListener)  # Add key release handler
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
