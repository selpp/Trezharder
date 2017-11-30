# Animation

# ===================================================
# ANIMATION

class Animation(object):
	def __init__(self, sprite_sheet, sprite_coords, duration, speed, loop = False):
		self.sprite_sheet = sprite_sheet
		self.sprite_coords = sprite_coords
		self.sprite_number = len(sprite_coords)
		self.duration = duration
		self.speed = speed
		self.rate = (1.0 * self.duration / self.sprite_number) * (1 / self.speed)
		self.loop = loop
		self.index = 0

	def next_frame(self):
		if self.index > self.sprite_number - 1:
			self.index = 0
		old_index = self.index
		row, col = self.sprite_coords[old_index]
		self.index += 1
		return self.sprite_sheet.get_sprite(row, col)

	def set_speed(self, speed):
		self.speed = speed
		self.rate = (1.0 * self.duration / self.sprite_number) * (1 / self.speed)

# ===================================================
# ANIMATOR

class Animator():
	def __init__(self):
		self.timer = 0
		self.anim_timer = 0
		self.animations = {}
		self.current_animation_id = None
		self.current_animation = None
		self.current_sprite = None
		self.current_animation_finished = False

	def add_animation(self, id, animation):
		if id in self.animations:
			return
		self.animations[id] = animation

	def set_animation(self, id):
		if id in self.animations:
			if self.current_animation_id == id:
				return
			self.current_animation_finished = False
			self.timer = 0
			self.anim_timer = 0
			self.current_animation_id = id
			self.current_animation = self.animations[id]
			self.current_sprite = self.current_animation.next_frame()

	def update(self, dt):
		self.timer += dt
		self.anim_timer += dt

		if self.current_animation is None:
			return 
		if self.current_animation.loop == False and self.timer > self.current_animation.duration:
			self.current_animation_finished = True
			return

		if self.anim_timer > self.current_animation.rate:
			self.anim_timer = 0
			self.current_sprite = self.current_animation.next_frame()

	def __str__(self):
		msg = 'Animator:\n  Animations: '
		msg += ' '.join(id for id in self.animations)
		return msg

	def state(self):
		msg = str(self)
		msg += '\n  id: ' + str(self.current_animation_id)
		msg += '\n  rate: ' + str(self.current_animation.rate)
		msg += '\n  timer: ' + str(self.timer)
		msg += '\n  anim_timer: ' + str(self.anim_timer)
		msg += '\n  anim_finished: ' + str(self.current_animation_finished)
		return msg

# ===================================================
# EXAMPLE: Animation system in action

if __name__ == '__main__':
	from pygame import display, event, KEYDOWN, KEYUP, K_z, K_q, K_s, K_d, K_LSHIFT
	from time import clock
	from data_manager import DataManager, SpriteSheetInfos

	data = DataManager()

	infos = SpriteSheetInfos(6, 4, (600/6, 400/4))
	data.load_sprite_sheet('TRUMP', 'TEST1.png', infos)
	spriteSheet = data.get_sprite_sheet('TRUMP')

	duration = 0.2
	speed = 1
	a_down = Animation(spriteSheet, [(i, 0) for i in range(6)], duration, speed, loop = True)
	a_right = Animation(spriteSheet, [(i, 1) for i in range(6)], duration, speed, loop = True)
	a_up = Animation(spriteSheet, [(i, 2) for i in range(6)], duration, speed, loop = True)
	a_left = Animation(spriteSheet, [(i, 3) for i in range(6)], duration, speed, loop = True)

	animator = Animator()
	animator.add_animation('DOWN', a_down)
	animator.add_animation('RIGHT', a_right)
	animator.add_animation('UP', a_up)
	animator.add_animation('LEFT', a_left)

	width = 800
	height = 600
	BLACK = (0, 0, 0)
	screen = display.set_mode((width, height))
	screen.fill(BLACK)

	current_time = clock()
	dt = 0

	animator.set_animation('DOWN')
	print animator.state()

	while True:
		events = event.get()
		for e in events:
			if e.type == KEYDOWN:
				if e.key == K_z:
					animator.set_animation('UP')
					animator.current_animation.set_speed(speed)
				elif e.key == K_s:
					animator.set_animation('DOWN')
					animator.current_animation.set_speed(speed)
				elif e.key == K_q:
					animator.set_animation('LEFT')
					animator.current_animation.set_speed(speed)
				elif e.key == K_d:
					animator.set_animation('RIGHT')
					animator.current_animation.set_speed(speed)
				elif e.key == K_LSHIFT:
					speed = 1.5
					animator.current_animation.set_speed(speed)
			if e.type == KEYUP:
				if e.key == K_LSHIFT:
					speed = 1
					animator.current_animation.set_speed(speed)

		screen.fill(BLACK)
		dt = clock() - current_time
		current_time += dt

		animator.update(dt)
		screen.blit(animator.current_sprite, (0, 0))

		display.flip()