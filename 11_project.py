from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
from ThreeD_OpenGL_Intro import draw_text

# ==================== GAME CONFIGURATION ====================
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
LANE_WIDTH = 200
VIEW_ANGLE = 100
OSCILLATION = math.sin(time.time() * 45) * 4

# ==================== GAME STATE ====================
view_mode = "third_person"
character_position = [0, 30, 0]
current_lane = 1  # 0: left, 1: center, 2: right
target_lane = 1   # target lane for smooth movement
lane_transition_active = False
lane_transition_speed = 8  # pixels per frame
camera_distance = 300
camera_rotation = 0

# Camera effects
camera_shake_active = False
camera_shake_start = 0
SHAKE_DURATION = 0.5
SHAKE_INTENSITY = 5

camera_zoom_active = False
camera_zoom_start = 0
ZOOM_DURATION = 0.5
ZOOM_SCALE = 0.8


game_ended = False
game_paused = False

# Adaptive difficulty
last_speed_increase_time = time.time()
SPEED_INCREASE_INTERVAL = 10   # seconds between difficulty increments
SPEED_INCREASE_AMOUNT = 0.2    # how much speed increases each step
MAX_SPEED = 20                 # cap speed so it's not impossible

# Movement and environment
path_offset = 0
movement_speed = 6

# Game objects collection
game_objects = []

# Visual elements
game_start_time = time.time()
last_color_update = game_start_time
path_colors = [0.5, 0.5, 0.8]

# Character physics
character_jumping = False
jump_velocity = 0
gravity = -0.9

# Platform interaction
on_platform = False
platform_end_z = 0

# Game progression
total_score = 0
remaining_lives = 5
platform_spawn_chance = 0.06
collectible_chance = 0.2

# Score multiplier system
combo_streak = 0
combo_multiplier = 1
last_collectible_time = 0
COMBO_TIMEOUT = 3  # seconds allowed between collectibles

# Object management
last_spawn_time = {0: -1, 1: -1, 2: -1}
min_spawn_distance = 200

# Special abilities
weapon_active_time = 0
projectile_position = None
projectile_speed = 50

# Power-up states
protection_active = False
protection_start_time = 0

weapon_equipped = False

speed_modified = False
speed_change_time = 0
base_speed = movement_speed

# Input tracking
input_history = []
MAX_INPUT_HISTORY = 10
status_message = ""
message_display_time = 0
MESSAGE_DURATION = 3

# Character customization
character_appearances = [
    {"torso": (0.4, 0.8, 0.7), "lower": (0.1, 0.1, 0.9)},
    {"torso": (0.9, 0.4, 0.4), "lower": (0.3, 0.3, 0.7)},
    {"torso": (0.7, 0.7, 0.3), "lower": (0.2, 0.5, 0.2)},
    {"torso": (0.6, 0.3, 0.8), "lower": (0.8, 0.4, 0.3)},
]
current_appearance = 0

# Special combinations
SPECIAL_COMBOS = {
    (101, 101): "protection",
    (103, 103): "weapon",
    (103, 101): "slow_time",
    (101, 103): "bonus_points",
}

character_rotation = 1
limb_movement_angle = 0
limb_movement_direction = 1

# Trees on the roadside
trees = []
TREE_SPAWN_CHANCE = 0.2   # 20% chance to spawn per cycle
TREE_DISTANCE = 800       # distance ahead of player to spawn trees

# Scenery objects
scenery_objects = []
SCENERY_SPAWN_CHANCE = 0.15  # 15% chance to spawn scenery per cycle
SCENERY_DISTANCE = 1000      # distance ahead of player to spawn scenery

# Scenery types and their properties
SCENERY_TYPES = {
    'building': {'width': 80, 'height': 150, 'depth': 60, 'color': (0.7, 0.7, 0.8)},
    'mountain': {'width': 200, 'height': 300, 'depth': 100, 'color': (0.5, 0.4, 0.3)},
    'rock': {'width': 40, 'height': 30, 'depth': 35, 'color': (0.6, 0.6, 0.6)},
    'bush': {'width': 25, 'height': 20, 'depth': 25, 'color': (0.2, 0.7, 0.2)},
    'billboard': {'width': 60, 'height': 80, 'depth': 5, 'color': (0.9, 0.9, 0.1)},
    'streetlight': {'width': 8, 'height': 120, 'depth': 8, 'color': (0.8, 0.8, 0.8)}
}

# Sky and distant background
SKY_COLOR = (0.5, 0.8, 1.0)  # Light blue sky
GROUND_COLOR = (0.3, 0.6, 0.2)  # Green ground


# ==================== CORE GAME FUNCTIONS ====================

def initialize_camera():
    """Configure the camera view and projection"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(VIEW_ANGLE, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if view_mode == "third_person":
        angle_rad = math.radians(camera_rotation)
        cam_x = character_position[0] + camera_distance * math.sin(angle_rad)
        cam_y = character_position[1] + 100
        cam_z = character_position[2] + camera_distance * math.cos(angle_rad)
        
        # Camera shake effect
        if camera_shake_active and time.time() - camera_shake_start < SHAKE_DURATION:
            cam_x += random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            cam_y += random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)

        # Camera zoom effect
        if camera_zoom_active and time.time() - camera_zoom_start < ZOOM_DURATION:
            cam_x *= ZOOM_SCALE
            cam_y *= ZOOM_SCALE
            cam_z *= ZOOM_SCALE


        gluLookAt(cam_x, cam_y, cam_z,
                 character_position[0], character_position[1], character_position[2],
                 0, 1, 0)
    else:
        head_height = 40
        look_ahead = 50
        
        eye_x = character_position[0]
        eye_y = character_position[1] + head_height + 30
        eye_z = character_position[2] - 5
        
        look_x = eye_x
        look_y = eye_y
        look_z = eye_z - look_ahead
        
        angle_rad = math.radians(camera_rotation)
        cam_x = character_position[0] + camera_distance * math.sin(angle_rad)
        cam_y = character_position[1] + 100
        cam_z = character_position[2] + camera_distance * math.cos(angle_rad)

        # Camera shake effect
        if camera_shake_active and time.time() - camera_shake_start < SHAKE_DURATION:
            cam_x += random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            cam_y += random.uniform(-SHAKE_INTENSITY, SHAKE_INTENSITY)

        # Camera zoom effect
        if camera_zoom_active and time.time() - camera_zoom_start < ZOOM_DURATION:
            cam_x *= ZOOM_SCALE
            cam_y *= ZOOM_SCALE
            cam_z *= ZOOM_SCALE

        gluLookAt(eye_x, eye_y, eye_z,
                 look_x, look_y, look_z,
                 0, 1, 0)

def create_environment():
    """Generate the game environment and path"""
    global path_offset, path_colors
    
    # Render sky and background
    render_sky_and_background()
    
    segment_size = 100
    total_segments = 1000
    
    for lane in range(3):
        lane_center = (lane - 1) * LANE_WIDTH
        
        for segment in range(total_segments):
            z_start = segment * segment_size - path_offset
            z_end = (segment + 1) * segment_size - path_offset
            
            # Alternate colors for visual pattern
            segment_color = path_colors if (segment + lane) % 2 == 0 else [1, 1, 1]
            glColor3f(*segment_color)
            
            glBegin(GL_QUADS)
            glVertex3f(lane_center - LANE_WIDTH/2, 0, -z_start)
            glVertex3f(lane_center + LANE_WIDTH/2, 0, -z_start)
            glVertex3f(lane_center + LANE_WIDTH/2, 0, -z_end)
            glVertex3f(lane_center - LANE_WIDTH/2, 0, -z_end)
            glEnd()
    
    # Draw roadside trees and scenery
    for tree in trees:
        render_tree(tree["x"], tree["z"] - path_offset)
    
    for scenery in scenery_objects:
        render_scenery_object(scenery)

def render_sky_and_background():
    """Render sky, distant mountains, and background elements"""
    # Disable depth testing for background
    glDisable(GL_DEPTH_TEST)
    
    # Render sky as a large quad
    glColor3f(*SKY_COLOR)
    glBegin(GL_QUADS)
    glVertex3f(-2000, 200, -3000)
    glVertex3f(2000, 200, -3000)
    glVertex3f(2000, 800, 3000)
    glVertex3f(-2000, 800, 3000)
    glEnd()
    
    # Render ground/grass on sides
    glColor3f(*GROUND_COLOR)
    glBegin(GL_QUADS)
    # Left side ground
    glVertex3f(-2000, 0, -3000)
    glVertex3f(-LANE_WIDTH*1.5, 0, -3000)
    glVertex3f(-LANE_WIDTH*1.5, 0, 3000)
    glVertex3f(-2000, 0, 3000)
    # Right side ground
    glVertex3f(LANE_WIDTH*1.5, 0, -3000)
    glVertex3f(2000, 0, -3000)
    glVertex3f(2000, 0, 3000)
    glVertex3f(LANE_WIDTH*1.5, 0, 3000)
    glEnd()
    
    # Render distant mountains
    render_distant_mountains()
    
    # Re-enable depth testing
    glEnable(GL_DEPTH_TEST)

def render_distant_mountains():
    """Render distant mountain silhouettes"""
    mountain_positions = [
        (-1500, -2000), (-800, -2200), (200, -1800), (900, -2500), (1600, -1900)
    ]
    
    for i, (x, z) in enumerate(mountain_positions):
        # Vary mountain heights and colors
        height = 400 + (i * 50) % 200
        color_variation = 0.1 + (i * 0.05) % 0.3
        
        glColor3f(0.3 + color_variation, 0.2 + color_variation, 0.4 + color_variation)
        
        # Draw mountain as triangle
        glBegin(GL_TRIANGLES)
        glVertex3f(x - 200, 0, z)
        glVertex3f(x + 200, 0, z)
        glVertex3f(x, height, z)
        glEnd()

def render_scenery_object(scenery):
    """Render various scenery objects"""
    x = scenery["x"]
    z = scenery["z"] - path_offset
    obj_type = scenery["type"]
    
    if z < -500 or z > 1500:  # Don't render if too far
        return
    
    props = SCENERY_TYPES[obj_type]
    
    glPushMatrix()
    glTranslatef(x, props['height'] / 2, -z)
    glColor3f(*props['color'])
    
    if obj_type == 'building':
        render_building(props)
    elif obj_type == 'mountain':
        render_small_hill(props)
    elif obj_type == 'rock':
        render_rock(props)
    elif obj_type == 'bush':
        render_bush(props)
    elif obj_type == 'billboard':
        render_billboard(props)
    elif obj_type == 'streetlight':
        render_streetlight(props)
    
    glPopMatrix()

def render_building(props):
    """Render a simple building"""
    # Main building structure
    glScalef(props['width']/30, props['height']/30, props['depth']/30)
    glutSolidCube(30)
    
    # Add some windows
    glColor3f(0.2, 0.2, 0.8)  # Blue windows
    for i in range(3):
        for j in range(4):
            glPushMatrix()
            glTranslatef(-12 + i*8, -5 + j*8, 16)
            glScalef(0.3, 0.3, 0.1)
            glutSolidCube(10)
            glPopMatrix()

def render_small_hill(props):
    """Render a small hill/mound"""
    glScalef(props['width']/50, props['height']/50, props['depth']/50)
    glutSolidSphere(50, 15, 10)

def render_rock(props):
    """Render a rock formation"""
    # Main rock
    glScalef(props['width']/25, props['height']/25, props['depth']/25)
    glutSolidSphere(25, 10, 8)
    
    # Add smaller rocks around it
    glColor3f(0.5, 0.5, 0.5)
    for i in range(3):
        angle = i * 120
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        glTranslatef(35, -10, 0)
        glScalef(0.6, 0.8, 0.6)
        glutSolidSphere(15, 8, 6)
        glPopMatrix()

def render_bush(props):
    """Render a bush with berries"""
    # Main bush body
    glScalef(props['width']/20, props['height']/20, props['depth']/20)
    glutSolidSphere(20, 12, 8)
    
    # Add some colorful berries
    glColor3f(0.8, 0.2, 0.2)  # Red berries
    for i in range(5):
        angle = i * 72
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        glTranslatef(15, 5, 0)
        glutSolidSphere(3, 6, 4)
        glPopMatrix()

def render_billboard(props):
    """Render a roadside billboard"""
    # Billboard post
    glColor3f(0.6, 0.4, 0.2)  # Brown post
    glPushMatrix()
    glTranslatef(0, -props['height']/4, 0)
    glScalef(0.2, 1, 0.2)
    glutSolidCube(props['height']/2)
    glPopMatrix()
    
    # Billboard surface
    glColor3f(*props['color'])
    glScalef(props['width']/30, props['height']/40, props['depth']/30)
    glutSolidCube(30)

def render_streetlight(props):
    """Render a streetlight"""
    # Post
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # Rotate to point upward
    glScalef(props['width']/20, props['width']/20, props['height']/20)
    quad = gluNewQuadric()
    gluCylinder(quad, 10, 8, 20, 8, 2)
    gluDeleteQuadric(quad)
    glPopMatrix()
    
    # Light fixture
    glColor3f(1, 1, 0.8)  # Light yellow
    glPushMatrix()
    glTranslatef(0, props['height']/2 - 10, 0)
    glutSolidSphere(12, 10, 8)
    glPopMatrix()


def create_character():
    """Render the player character with animations"""
    global character_rotation, limb_movement_angle, limb_movement_direction, current_appearance, character_position
    global lane_transition_active, target_lane, current_lane, lane_transition_speed
    
    # Handle smooth lane transitions
    target_x = (target_lane - 1) * LANE_WIDTH
    
    if lane_transition_active:
        # Calculate direction and move towards target
        if abs(character_position[0] - target_x) > lane_transition_speed:
            if character_position[0] < target_x:
                character_position[0] += lane_transition_speed
            else:
                character_position[0] -= lane_transition_speed
        else:
            # Transition complete
            character_position[0] = target_x
            current_lane = target_lane
            lane_transition_active = False
    else:
        # Ensure character is in correct position when not transitioning
        character_position[0] = target_x
    
    torso_color = character_appearances[current_appearance]["torso"]
    legs_color = character_appearances[current_appearance]["lower"]
    
    glPushMatrix()
    glTranslatef(*character_position)
    
    # Orient character properly
    glRotatef(-90, 1, 0, 0)
    glRotatef(90, 0, 0, 1)
    
    if game_ended:
        glRotatef(90, 1, 0, 0)
    
    # Animate limbs when moving
    if not game_ended and not character_jumping:
        limb_movement_angle += limb_movement_direction * 2
        if abs(limb_movement_angle) > 30:
            limb_movement_direction *= -1
    else:
        limb_movement_angle = 0
    
    # Character body
    glColor3f(*torso_color)
    glutSolidCube(30)
    
    # Legs with animation
    glPushMatrix()
    glTranslatef(0, -15, 0)
    glRotatef(180 + limb_movement_angle, 0, 1, 0)
    glColor3f(*legs_color)
    gluCylinder(gluNewQuadric(), 10, 4, 40, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 15, 0)
    glRotatef(180 - limb_movement_angle, 1, 1, 0)
    glColor3f(*legs_color)
    gluCylinder(gluNewQuadric(), 10, 4, 40, 10, 10)
    glPopMatrix()
    
    # Arms
    glPushMatrix()
    glTranslatef(0, 20, 20)
    glRotatef(90, 0, 1, 0)
    glColor3f(0.8, 0.6, 0.6)
    gluCylinder(gluNewQuadric(), 10, 4, 40, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, -20, 20)
    glRotatef(90, 0, 1, 0)
    glColor3f(0.8, 0.6, 0.6)
    gluCylinder(gluNewQuadric(), 10, 4, 40, 10, 10)
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glColor3f(0, 0, 0)
    glutSolidSphere(15, 20, 20)
    glPopMatrix()
    
    # Weapon if active
    if weapon_equipped:
        glPushMatrix()
        glTranslatef(0, 0, 30)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.5, 0.5, 0.5)   # grey
        gluCylinder(gluNewQuadric(), 10, 3, 60, 10, 10)
        glPopMatrix()
    
    glPopMatrix()

def create_game_objects():
    """Render all game objects and handle interactions"""
    global on_platform, platform_end_z, character_position, path_offset, remaining_lives
    global character_jumping, total_score
    global OSCILLATION, game_objects
    
    for obj in game_objects[:]:
        obj_x = (obj['lane'] - 1) * LANE_WIDTH
        obj_z = obj['z_start'] - path_offset
        
        # Render based on object type
        render_object(obj, obj_x, obj_z)
        
        # Handle special object interactions
        if obj['type'] == 'platform' and obj['has_ramp']:
            render_ramp(obj, obj_x, obj_z)
            handle_ramp_collision(obj, obj_x)
        
        # Remove distant objects
        if obj['z_start'] < path_offset - 200:
            game_objects.remove(obj)
    
    handle_platform_exit()

def render_object(obj, x, z):
    """Render a game object based on its type"""
    obj_type = obj['type']
    
    if obj_type == 'collectible':
        render_collectible(obj, x, z)
    elif obj_type == 'platform':
        render_platform(obj, x, z)
    elif obj_type == 'barrier':
        render_barrier(obj, x, z)
    elif obj_type == 'explosive':
        render_explosive(obj, x, z)
    elif obj_type == 'protection':
        render_protection_powerup(obj, x, z)
    elif obj_type == 'speed_boost':
        render_speed_powerup(obj, x, z)
    elif obj_type == 'weapon_powerup':
        render_weapon_powerup(obj, x, z)

def render_collectible(obj, x, z):
    """Render collectible items"""
    glColor3f(1, 0.98, 0)
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2, -z - obj['length'] / 2)
    glScalef(1, obj['height'] / 30, obj['length'] / 30)
    glutSolidSphere(30, 30, 30)
    glPopMatrix()

def render_platform(obj, x, z):
    """Render platform objects"""
    if obj['has_ramp']:
        glColor3f(0.2, 0.4, 0.8)
    else:
        glColor3f(0.8, 0.4, 0.1)
    
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2, -z - obj['length'] / 2)
    glScalef(1, obj['height'] / 30, obj['length'] / 30)
    glutSolidCube(30)
    glPopMatrix()

def render_barrier(obj, x, z):
    """Render barrier objects"""
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2, -z - obj['length'] / 2)
    glScalef(4, obj['height'] / 30, obj['length'] / 30)
    glutSolidCube(30)
    glPopMatrix()

def render_explosive(obj, x, z):
    """Render explosive objects with animation"""
    current_time = time.time()
    scale = 0.8 + 0.4 * math.sin(current_time * 3)
    OSCILLATION = math.sin(current_time * 2) * 10
    
    glColor3f(1, 0, 1)
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2 + OSCILLATION, -z - obj['length'] / 2)
    glScalef(scale, scale, scale)
    glutSolidSphere(30, 30, 30)
    glPopMatrix()

def render_protection_powerup(obj, x, z):
    """Render protection power-ups"""
    current_time = time.time()
    scale = 1 + 0.2 * math.sin(current_time * 3)
    OSCILLATION = math.sin(current_time * 2) * 10
    
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2 + OSCILLATION, -z - obj['length'] / 2)
    glScalef(scale, scale, scale)
    
    glColor3f(0, 1, 0)
    glRotatef(90, 0, 1, 0)
    glRotatef(90, 1, 0, 0)
    gluDisk(gluNewQuadric(), 5, 30, 30, 1)
    
    glTranslatef(0, 0, 1)
    glColor3f(1, 1, 1)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    
    glPopMatrix()

def render_speed_powerup(obj, x, z):
    """Render speed power-ups"""
    current_time = time.time()
    scale = 1 + 0.2 * math.sin(current_time * 3)
    global OSCILLATION
    
    glColor3f(0, 0, 1)
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2 + OSCILLATION, -z - obj['length'] / 2)
    glScalef(scale, scale, scale)
    glutSolidCube(30)
    glPopMatrix()

def render_weapon_powerup(obj, x, z):
    """Render weapon power-ups"""
    current_time = time.time()
    scale = 0.8 + 0.4 * math.sin(current_time * 3)
    global OSCILLATION

    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(x, obj['height'] / 2 + OSCILLATION, -z - obj['length'] / 2)
    glScalef(scale, scale, scale)
    glutSolidCylinder(30, 30, 30, 30)
    glPopMatrix()

def render_ramp(obj, x, z):
    """Render ramp for platform objects"""
    glColor3f(0.9, 0.9, 0.2)
    glBegin(GL_TRIANGLES)
    glVertex3f(x - LANE_WIDTH / 2, 0, -z - 5)
    glVertex3f(x + LANE_WIDTH / 2, 0, -z - 5)
    glVertex3f(x, obj['height'], -z - 5)
    glEnd()

def render_tree(x, z):
    """Render an upright tree with trunk + leaves (trunk points upward along +Y)"""
    glPushMatrix()
    # position tree base on the ground
    glTranslatef(x, 0, -z)

    # Draw trunk: rotate GLU cylinder (which points along +Z) to point up (+Y)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  # rotate so cylinder's axis becomes +Y
    glColor3f(0.45, 0.25, 0.07)
    quad = gluNewQuadric()
    gluCylinder(quad, 6, 4, 60, 12, 2)  # base_radius, top_radius, height
    gluDeleteQuadric(quad)
    glPopMatrix()

    # Draw leaves on top of the trunk
    glTranslatef(0, 60, 0)  # move up by trunk height
    glColor3f(0.0, 0.6, 0.0)
    glutSolidSphere(25, 20, 20)

    glPopMatrix()


def handle_ramp_collision(obj, x):
    """Handle collision with ramp objects"""
    global on_platform, platform_end_z, character_position
    
    ramp_start = obj['z_start']
    activation_range = 20
    
    player_x, player_z = character_position[0], character_position[2]
    
    if (abs(player_x - x) < LANE_WIDTH / 2 and
            ramp_start - path_offset < player_z + activation_range < ramp_start - path_offset + activation_range and
            not character_jumping):
        
        on_platform = True
        platform_end_z = obj['z_start'] + obj['length'] * 2
        character_position[1] = obj['height'] + 30

def handle_platform_exit():
    """Handle exiting platform objects"""
    global on_platform, character_position
    
    if on_platform and character_position[2] < -(platform_end_z - path_offset):
        on_platform = False
        character_position[1] = 30

def display_game():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    initialize_camera()
    create_environment()
    create_character()
    create_game_objects()
    
    # Display game information
    draw_text(10, SCREEN_HEIGHT - 20, f"Score: {total_score}")
    draw_text(10, SCREEN_HEIGHT - 50, f"Lives: {remaining_lives}")
    draw_text(10, SCREEN_HEIGHT - 400, f"Speed: {movement_speed:.1f}")

    if combo_multiplier > 1:
        draw_text(10, SCREEN_HEIGHT - 80, f"Combo x{combo_multiplier}")
    
    if game_ended:
        draw_text(SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT/2, "Game Over!")
        draw_text(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 30, "Press 'R' to Restart")
    elif game_paused:
        draw_text(SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT/2, "Game Paused")
    
    if projectile_position:
        glPushMatrix()
        glColor3f(1, 0, 0)
        glTranslatef(projectile_position[0], projectile_position[1], projectile_position[2])
        glutSolidCube(10)
        glPopMatrix()
    
    if protection_active:
        remaining = max(0, 5 - int(time.time() - protection_start_time))
        draw_text(10, SCREEN_HEIGHT - 110, f"Shield: {remaining}s")
    
    if speed_modified:
        remaining = max(0, 5 - int(time.time() - speed_change_time))
        draw_text(10, SCREEN_HEIGHT - 140, f"Slow: {remaining}s")
    
    if weapon_equipped:
        remaining = max(0, 5 - int(time.time() - weapon_active_time))
        draw_text(10, SCREEN_HEIGHT - 170, f"Weapon: {remaining}s")
    
    if status_message and time.time() - message_display_time < MESSAGE_DURATION:
        draw_text(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 100, status_message)
    
    glutSwapBuffers()

def reset_game_state():
    """Reset the game to initial state"""
    global game_ended, path_offset, game_objects, total_score, remaining_lives, character_jumping, character_position
    global on_platform, platform_end_z, protection_active, weapon_equipped, projectile_position
    global speed_modified, movement_speed, base_speed, protection_start_time, weapon_active_time
    global current_lane, target_lane, lane_transition_active, trees, scenery_objects
    
    game_ended = False
    total_score, remaining_lives = 0, 5
    character_jumping = False
    game_objects.clear()
    trees.clear()
    scenery_objects.clear()  # Clear scenery objects
    path_offset = 0
    character_position = [0, 30, 0]
    current_lane = 1
    target_lane = 1
    lane_transition_active = False
    
    on_platform = False
    platform_end_z = 0
    
    protection_active = False
    protection_start_time = 0
    
    speed_modified = False
    speed_change_time = 0
    movement_speed = base_speed
    
    weapon_equipped = False
    weapon_active_time = 0
    projectile_position = None

def handle_keyboard(key, x, y):
    """Handle keyboard input"""
    global current_lane, target_lane, lane_transition_active, character_jumping, jump_velocity, game_paused, game_ended
    global view_mode, weapon_equipped, projectile_position, camera_rotation
    global current_appearance
    
    if key == b'r' and game_ended:
        reset_game_state()
        return
    
    # Only allow lane changes if not already transitioning
    if key == b'a' and target_lane > 0 and not lane_transition_active:
        target_lane -= 1
        lane_transition_active = True
    elif key == b'd' and target_lane < 2 and not lane_transition_active:
        target_lane += 1
        lane_transition_active = True
    elif key == b' ' and not character_jumping:
        character_jumping = True
        jump_velocity = 10
    elif key == b'x':
        game_paused = not game_paused
    elif key == b'e':
        camera_rotation += 5
    elif key == b'q':
        camera_rotation -= 5
    elif key == b'v':
        current_appearance = (current_appearance + 1) % len(character_appearances)

def handle_special_keys(key, x, y):
    """Handle special key input and combo detection"""
    global current_lane, target_lane, lane_transition_active, input_history
    
    # Only allow lane changes if not already transitioning
    if key == GLUT_KEY_LEFT and target_lane > 0 and not lane_transition_active:
        target_lane -= 1
        lane_transition_active = True
    elif key == GLUT_KEY_RIGHT and target_lane < 2 and not lane_transition_active:
        target_lane += 1
        lane_transition_active = True
    
    input_history.append(key)
    if len(input_history) > MAX_INPUT_HISTORY:
        input_history.pop(0)
    
    detect_special_combos()

def detect_special_combos():
    """Detect and activate special combinations"""
    global input_history
    
    for combo, action in SPECIAL_COMBOS.items():
        recent_keys = tuple(input_history[-len(combo):])
        if recent_keys == combo:
            activate_special_action(action)
            input_history.clear()
            break

def activate_special_action(action):
    """Activate special game actions"""
    global remaining_lives, total_score, protection_active, protection_start_time
    global weapon_equipped, weapon_active_time, speed_modified, speed_change_time, movement_speed, base_speed
    global status_message, message_display_time
    
    if action == "protection":
        protection_active = True
        protection_start_time = time.time()
        status_message = "SPECIAL: Protection Activated"
    elif action == "weapon":
        weapon_equipped = True
        weapon_active_time = time.time()
        status_message = "SPECIAL: Weapon Activated"
    elif action == "slow_time":
        if not speed_modified:
            speed_modified = True
            speed_change_time = time.time()
            movement_speed = max(1, movement_speed - 2)
            status_message = "SPECIAL: Slow Motion"
    elif action == "bonus_points":
        total_score += 100
        remaining_lives += 1
        status_message = "SPECIAL: +100 Points, +1 Life"
    
    message_display_time = time.time()

def handle_mouse_input(button, state, x, y):
    """Handle mouse input"""
    global projectile_position, view_mode
    
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            if weapon_equipped and not projectile_position:
                projectile_position = [character_position[0], character_position[1], character_position[2]]
        elif button == GLUT_RIGHT_BUTTON:
            view_mode = "first_person" if view_mode == "third_person" else "third_person"

def update_path_colors():
    """Update path colors periodically"""
    global path_colors, last_color_update
    
    current_time = time.time()
    if current_time - last_color_update >= 30:
        path_colors = [random.random() for _ in range(3)]
        last_color_update = current_time

def generate_new_objects():
    """Generate new game objects dynamically"""
    global last_spawn_time, platform_spawn_chance, collectible_chance, game_objects, min_spawn_distance
    
    lanes = [0, 1, 2]
    min_gap = 250
    
    def is_position_available(z, lane):
        return all(
            abs(obj['z_start'] - z) > min_gap or obj['lane'] != lane
            for obj in game_objects
        )
    
    active_lanes = {obj['lane'] for obj in game_objects if path_offset < obj['z_start'] < path_offset + 500}
    if len(active_lanes) >= 2:
        return
    
    existing_types = {
        obj_type: any(obj['type'] == obj_type and path_offset < obj['z_start'] < path_offset + 500 for obj in game_objects)
        for obj_type in ['platform', 'collectible', 'barrier', 'explosive', 'protection', 'speed_boost', 'weapon_powerup']
    }
    
    def add_object(lane, z_pos, length, height, obj_type, has_ramp=False):
        game_objects.append({
            'lane': lane,
            'z_start': z_pos,
            'length': length,
            'height': height,
            'type': obj_type,
            'has_ramp': has_ramp
        })
        if obj_type in ['collectible', 'explosive', 'protection', 'speed_boost', 'weapon_powerup']:
            last_spawn_time[lane] = path_offset
    
    # Generate different types of objects based on probabilities
    if not existing_types['collectible'] and random.random() < platform_spawn_chance:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        base_z = path_offset + 800
        for i in range(random.choice([3, 4])):
            z_pos = base_z + i * 200
            if is_position_available(z_pos, lane):
                add_object(lane, z_pos, 200, 100, 'platform', has_ramp=(i == 0))
    
    elif not existing_types['platform'] and random.random() < collectible_chance:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        z_pos = path_offset + 600 + random.randint(0, 100)
        if is_position_available(z_pos, lane) and path_offset - last_spawn_time[lane] > min_spawn_distance:
            add_object(lane, z_pos, 30, 40, 'collectible')
    
    elif not existing_types['barrier'] and random.random() < collectible_chance:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        z_pos = path_offset + 600 + random.randint(0, 100)
        if is_position_available(z_pos, lane) and path_offset - last_spawn_time[lane] > min_spawn_distance:
            add_object(lane, z_pos, 40, 30, 'barrier')
    
    elif not existing_types['explosive'] and random.random() < 0.1:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        z_pos = path_offset + 600 + random.randint(0, 100)
        if is_position_available(z_pos, lane) and path_offset - last_spawn_time[lane] > min_spawn_distance:
            add_object(lane, z_pos, 30, 30, 'explosive')
    
    elif not existing_types['protection'] and random.random() < 0.1:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        z_pos = path_offset + 600 + random.randint(0, 100)
        if is_position_available(z_pos, lane) and path_offset - last_spawn_time[lane] > min_spawn_distance:
            add_object(lane, z_pos, 30, 40, 'protection')
    
    elif not existing_types['speed_boost'] and random.random() < 0.1:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        z_pos = path_offset + 600 + random.randint(0, 100)
        if is_position_available(z_pos, lane) and path_offset - last_spawn_time[lane] > min_spawn_distance:
            add_object(lane, z_pos, 30, 40, 'speed_boost')
    
    elif not existing_types['weapon_powerup'] and random.random() < 0.1:
        lane = random.choice([l for l in lanes if l not in active_lanes])
        z_pos = path_offset + 600 + random.randint(0, 100)
        if is_position_available(z_pos, lane) and path_offset - last_spawn_time[lane] > min_spawn_distance:
            add_object(lane, z_pos, 30, 40, 'weapon_powerup')

def generate_trees():
    """Randomly generate trees along both sides of the lanes"""
    global trees, path_offset

    if random.random() < TREE_SPAWN_CHANCE:
        side = random.choice([-1, 1])  # left or right side
        x_offset = (LANE_WIDTH * 2) * side  # place outside the lanes
        z_pos = path_offset + TREE_DISTANCE + random.randint(0, 200)
        trees.append({"x": x_offset, "z": z_pos})
    
    # Remove old trees
    trees = [t for t in trees if t["z"] > path_offset - 200]

def generate_scenery():
    """Generate various scenery objects around the game world"""
    global scenery_objects, path_offset
    
    if random.random() < SCENERY_SPAWN_CHANCE:
        # Choose random scenery type
        scenery_type = random.choice(list(SCENERY_TYPES.keys()))
        
        # Position scenery further from road than trees
        side = random.choice([-1, 1])  # left or right side
        
        # Vary distance from road based on object type
        if scenery_type in ['building', 'mountain']:
            x_offset = (LANE_WIDTH * 3 + random.randint(50, 200)) * side
        elif scenery_type == 'streetlight':
            x_offset = (LANE_WIDTH * 1.8) * side  # Closer to road
        else:
            x_offset = (LANE_WIDTH * 2.5 + random.randint(0, 100)) * side
        
        z_pos = path_offset + SCENERY_DISTANCE + random.randint(0, 300)
        
        scenery_objects.append({
            "x": x_offset,
            "z": z_pos,
            "type": scenery_type
        })
    
    # Remove old scenery objects
    scenery_objects = [s for s in scenery_objects if s["z"] > path_offset - 500]


def game_loop():
    """Main game loop update function"""
    global path_offset, total_score, remaining_lives, game_ended, game_paused, character_jumping, jump_velocity
    global projectile_position, projectile_speed, movement_speed, protection_active, protection_start_time
    global weapon_equipped, weapon_active_time, speed_modified, speed_change_time, base_speed, gravity
    global game_objects
    
    if game_ended or game_paused:
        return
    
    path_offset += movement_speed
    update_path_colors()
    generate_new_objects()
    generate_trees()
    generate_scenery()  # Add scenery generation
    
    # Handle character jumping
    if character_jumping:
        character_position[1] += jump_velocity
        jump_velocity += gravity
        if character_position[1] <= 30:
            character_position[1] = 30
            character_jumping = False
    
    # Handle object collisions
    for obj in game_objects[:]:
        obj_z = obj['z_start'] - path_offset
        obj_x = (obj['lane'] - 1) * LANE_WIDTH
        player_x, player_z = character_position[0], character_position[2]
        
        distance_x = abs(player_x - obj_x)
        distance_z = abs(player_z + obj_z)
        collision = distance_x < 40 and distance_z < obj['length'] / 2 and character_position[1] <= obj['height'] + 10
        
        if collision:
            handle_collision(obj)
    
    # Handle projectile movement and collisions
    if weapon_equipped and projectile_position:
        projectile_position[2] -= projectile_speed
        
        for obj in game_objects[:]:
            if obj['type'] in ['barrier', 'platform']:
                obj_x = (obj['lane'] - 1) * LANE_WIDTH
                obj_z = obj['z_start'] - path_offset
                if abs(projectile_position[0] - obj_x) < 40 and abs(-projectile_position[2] - obj_z) < obj['length'] / 2:
                    game_objects.remove(obj)
                    projectile_position = None
                    break
        
        if projectile_position and projectile_position[2] < -2000:
            projectile_position = None
        
        if weapon_equipped and time.time() - weapon_active_time > 5:
            weapon_equipped = False
    
    # Handle power-up expiration
    if protection_active and time.time() - protection_start_time > 5:
        protection_active = False
        protection_start_time = 0
    
    if speed_modified and time.time() - speed_change_time > 5:
        speed_modified = False
        speed_change_time = 0
        movement_speed = base_speed
    
    if weapon_equipped and time.time() - weapon_active_time > 10:
        weapon_equipped = False
        weapon_active_time = 0
        projectile_position = None
    
    # Adaptive difficulty: speed increases every fixed interval
    global last_speed_increase_time
    current_time = time.time()
    if current_time - last_speed_increase_time >= SPEED_INCREASE_INTERVAL:
        movement_speed = min(MAX_SPEED, movement_speed + SPEED_INCREASE_AMOUNT)
        last_speed_increase_time = current_time
    
    glutPostRedisplay()

def handle_collision(obj):
    """Handle collisions with different object types"""
    global total_score, remaining_lives, protection_active, game_objects
    global speed_modified, movement_speed, speed_change_time, weapon_equipped, weapon_active_time
    
    obj_type = obj['type']
    
    if obj_type == 'explosive':
        total_score += random.randint(10, 100)
        game_objects.remove(obj)
    elif obj_type == 'protection':
        protection_active = True
        protection_start_time = time.time()
        game_objects.remove(obj)
    elif obj_type == 'speed_boost':
        if not speed_modified:
            speed_modified = True
            speed_change_time = time.time()
            movement_speed = max(1, movement_speed - 2)
        game_objects.remove(obj)
    elif obj_type == 'weapon_powerup':
        weapon_equipped = True
        weapon_active_time = time.time()
        game_objects.remove(obj)
    elif obj_type == 'collectible':
        #total_score += 5

        global combo_streak, combo_multiplier, last_collectible_time
    
        current_time = time.time()
        if current_time - last_collectible_time <= COMBO_TIMEOUT:
            combo_streak += 1
        else:
            combo_streak = 1  # reset streak
        
        combo_multiplier = 1 + (combo_streak // 3)  # every 3 streak increases multiplier
        total_score += 5 * combo_multiplier
        
        last_collectible_time = current_time
        game_objects.remove(obj)

    elif obj_type in ['platform', 'barrier'] and not obj.get('has_ramp'):
        if not protection_active:
            remaining_lives -= 1

            # Trigger camera effects
            global camera_shake_active, camera_shake_start, camera_zoom_active, camera_zoom_start
            camera_shake_active = True
            camera_shake_start = time.time()
            camera_zoom_active = True
            camera_zoom_start = time.time()
        
        game_objects.remove(obj)
    
    if remaining_lives <= 0:
        game_ended = True

def main():
    """Main game initialization"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow(b"Lane Legend: Obstacle Odyssey")
    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(display_game)
    glutKeyboardFunc(handle_keyboard)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse_input)
    glutIdleFunc(game_loop)
    
    glutMainLoop()

if __name__ == "__main__":
    main()