from data_manager import DataManager, SpriteSheetInfos
from animation import Animation, Animator
from monobehaviour import MonoBehaviour
#from fsm import State, FSM
from vector import Vector
from collider import BoxCollider
from game_engine import GameEngineTools

class PlayerTest(MonoBehaviour):
    def __init__(self,Command):
        MonoBehaviour.__init__(self,1)

    def start(self):
    	# ================= State Machine =========================  
		#self.state_machine = PlayerFSM()
		self.ennemies = GameEngineTools.find_all('player')
  
		# ================= Transform =========================
		self.transform.get_scale().x = 100
		self.transform.get_scale().y = 100
		self.transform.tag = 'player'
		self.velocity = Vector(0.0, 0.0)      

		# ================= Collider ==========================
		self.gameobject.rigidbody.set_collider(BoxCollider(None , self.transform, Vector(0.0, 25.0), Vector(0.3, 0.3) , self.gameobject))

		# ================= Animator ==========================
		self.animator = Animator()

		scale = self.transform.get_scale()
		infos = SpriteSheetInfos(6, 4, (scale.x, scale.y))
  		data_manager = DataManager.get_instance()
		data_manager.load_sprite_sheet('TRUMP', 'TEST1.png', infos)
		spriteSheet = data_manager.get_sprite_sheet('TRUMP')
		duration = 0.6		
		a_down = Animation(spriteSheet, [(i, 0) for i in range(6)], duration, 1, loop = True)
		a_right = Animation(spriteSheet, [(i, 1) for i in range(6)], duration, 1, loop = True)
		a_up = Animation(spriteSheet, [(i, 2) for i in range(6)], duration, 1, loop = True)
		a_left = Animation(spriteSheet, [(i, 3) for i in range(6)], duration, 1, loop = True)
		a_idle_down = Animation(spriteSheet, [(1, 0)], duration, 1, loop = True)
		a_idle_right = Animation(spriteSheet, [(1, 1)], duration, 1, loop = True)
		a_idle_up = Animation(spriteSheet, [(1, 2)], duration, 1, loop = True)
		a_idle_left = Animation(spriteSheet, [(1, 3)], duration, 1, loop = True)

		self.animator.add_animation('DOWN', a_down)
		self.animator.add_animation('RIGHT', a_right)
		self.animator.add_animation('UP', a_up)
		self.animator.add_animation('LEFT', a_left)
		self.animator.add_animation('IDLE_DOWN', a_idle_down)
		self.animator.add_animation('IDLE_RIGHT', a_idle_right)
		self.animator.add_animation('IDLE_UP', a_idle_up)
		self.animator.add_animation('IDLE_LEFT', a_idle_left)
		
    def update(self, dt):
		self.animator.update(dt)
		self.state_machine.update(dt, self)

    def fixed_update(self, fixed_dt):
		self.state_machine.fixed_update(fixed_dt, self)

    def draw(self, screen):
        scale = self.transform.get_scale() / 2.0
        draw_pos = self.transform.get_position() - scale
        screen.blit(self.animator.current_sprite, (draw_pos.x, draw_pos.y))
        
    def die(self):
        print('I died')
        GameEngineTools.DestroyObject(self.gameobject)

    def z_buff(self, z_index, z_buffer):
    	z_buffer.insert(z_index, self)
    
    