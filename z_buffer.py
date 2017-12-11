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

	def draw_ai(self, screen):
		self.value.draw_ai(screen)

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

	def draw(self, screen):
		self.content.sort(key = lambda x:x.value.transform.get_position().y)
		for element in self.content:
			element.draw(screen)

	def draw_ai(self, screen):
		self.content.sort(key = lambda x:x.value.transform.get_position().y)
		for element in self.content:
			element.draw_ai(screen)

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


	def draw(self, screen):
		self.z_lists.sort(key = lambda x: x.z_index)
		for z_list in self.z_lists:
			z_list.draw(screen)

	def draw_ai(self, screen):
		self.z_lists.sort(key = lambda x: x.z_index)
		for z_list in self.z_lists:
			z_list.draw_ai(screen)