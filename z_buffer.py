# Z Buffer

# ===================================================
# ZELEMENT

class ZElement(object):
	def __init__(self, value):
		self.value = value

	def __eq__(self, other):
		return self.value == other.value

	def draw(self, screen):
		self.value.draw(screen)

# ===================================================
# ZLIST

class ZList(object):
	def __init__(self, z_index, is_dynamic = False):
		self.z_index = z_index
		self.content = []
		self.is_dynamic = is_dynamic

	def insert(self, value):
		element = ZElement(value)
		self.content.append(element)
		self.content.sort(key = lambda x:x.value.transform.get_position().y)

	def draw(self, screen):
		for element in self.content:
			element.draw(screen)

# ===================================================
# ZBUFFER

class ZBuffer(object):
	def __init__(self):
		self.z_lists = []

	def reset(self):
		self.z_lists = []

	def insert(self, z_index, value, is_dynamic = False):
		for z_list in self.z_lists:
			if z_list.z_index == z_index:
				z_list.insert(value)
				return
		z_list = ZList(z_index, is_dynamic)
		z_list.insert(value)
		self.z_lists.append(z_list)
		self.z_lists.sort(key = lambda x: x.z_index)

	def draw(self, screen):
		for z_list in self.z_lists:
			z_list.draw(screen)

# ===================================================
# EXAMPLE

if __name__ == '__main__':
	from transform import Transform
	from vector import Vector
	from pygame import display
	from time import clock

	import os 

	class Test(object):
		def __init__(self, val, pos):
			self.val = val
			self.transform = Transform(Vector(pos.x, pos.y), 0.0, Vector(1.0, 1.0))

	e0 = Test('{z_index: 0, y: 1}', Vector(0, 1))
	e4 = Test('{z_index: 2, y: 2}', Vector(0, 2))
	e3 = Test('{z_index: 2, y: 1}', Vector(0, 1))
	e1 = Test('{z_index: 0, y: 2}', Vector(0, 2))
	e2 = Test('{z_index: 0, y: 3}', Vector(0, 3))
	e5 = Test('{z_index: 2, y: 3}', Vector(0, 3))
	e6 = Test('{z_index: 1, y: 3}', Vector(0, 2))

	z_buffer = ZBuffer()

	z_buffer.insert(0, e0)
	z_buffer.insert(2, e4)
	z_buffer.insert(2, e3)
	z_buffer.insert(0, e1)
	z_buffer.insert(0, e2)
	z_buffer.insert(2, e5)
	z_buffer.insert(1, e6)

	current_time = clock()
	dt = 0

	while True:
		dt = clock() - current_time
		current_time += dt

		if current_time % 1 == 0:
			os.system('clear')

			z_buffer.reset()
			
			z_buffer.insert(0, e0)
			z_buffer.insert(2, e4)
			z_buffer.insert(2, e3)
			z_buffer.insert(0, e1)
			z_buffer.insert(0, e2)
			z_buffer.insert(2, e5)
			z_buffer.insert(1, e6)

			for z_list in z_buffer.z_lists:
				for element in z_list.content:
					print str(element.value.val) + '\n'
