from pygame import display, event, font
from time import clock, sleep
from data_manager import DataManager
from physics_manager import PhysicsManager
from input_manager import InputManager
from z_buffer import ZBuffer
from map_manager import MapManager
from player import Player
from bot import Bot
from random import randint

# ===== SCREEN ==================
width = 800
height = 600
BLACK = (0, 0, 0)
screen = display.set_mode((width, height))
screen.fill(BLACK)

# ===== ENTITIES ================
data = DataManager()    
z_buffer = ZBuffer()

player = Player(data)
player.transform.get_position().x = 6 * 100.0 + 50.0
player.transform.get_position().y = 4 * 100.0 + 50.0

bot = Bot(data)
bot.transform.get_position().x = 100.0 + 50.0
bot.transform.get_position().y = 100.0 + 50.0

map_manager = MapManager(data)
map_manager.load(path = 'MAP0.map')

# ===== DELTA TIME ==============
current_time = clock()
dt = 0

# ===== FPS =====================
fps_cap = 60
fps = 60
fps_cumulator = 0
fps_timer = 0
font.init()
fps_font = font.SysFont("monospace", 30)

def show_fps(fps):
    fps_label = fps_font.render('FPS: ' + str(fps), 1, (0, 255, 0))
    screen.blit(fps_label, (0, 0))

# ===== FIXED DELTA TIME ========
current_fixed_time = clock()
fixed_dt = 0
fixed_timer = 0
fixed_rate = 0.02

time_scale = 1.0

# ===== GET PhysicsManager ========
pm = PhysicsManager.get_instance()

# ===== Random Bot actions ========
bot_timer = 0
# v_x, v_y, shift, fire1
bot_action = [1, 0, 1, 0]
bot.action_vector = bot_action

# ===== LOOP ====================
while True:
    InputManager.get_instance().update(event.get())

    screen.fill(BLACK)
    z_buffer.reset()

    # ====================================================================
    # ===== Update =====
    dt = (clock() - current_time) * time_scale
    current_time += dt
    
    fps_timer += dt
    fps_cumulator += 1
    if fps_timer > 1:
        fps = fps_cumulator
        fps_cumulator = 0
        fps_timer = 0

    # ===== Bot ========
    bot_timer += dt

    # ===== Update =====
    player.update(dt)
    bot.update(dt)

    if bot_timer > 1:
		bot_timer = 0
		# v_x, v_y, shift, fire1
		bot_action = [round(randint(-1, 1)), round(randint(-1, 1)), randint(0, 1), randint(0, 1)]
		bot.action_vector = bot_action

    # ===== FixedUpdate =====
    fixed_timer += dt
    if fixed_timer > fixed_rate:
        fixed_timer = 0
        fixed_dt = clock() - current_fixed_time
        current_fixed_time += fixed_dt

        player.fixed_update(fixed_dt)
        bot.fixed_update(fixed_dt)
        pm.update_collision()

    # ===== Draw =====
    map_manager.z_buff(0, z_buffer)
    player.z_buff(2, z_buffer)
    bot.z_buff(2, z_buffer)

    z_buffer.draw(screen)

    # ====================================================================
    show_fps(fps)

    display.flip()  