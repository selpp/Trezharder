# Debug Drawings 
from pygame import draw

# ===================================================
# DEBUGDRAWINGS

class DebugDrawings(object):
	@staticmethod
	def draw_circle(screen, position, radius, color):
		draw.circle(screen, color, (position.x, position.y), radius, 2)

	@staticmethod
	def draw_rect(screen, position, width, height, color):
		draw.rect(screen, color, (position.x - width / 2.0, position.y - height / 2.0, width, height), 2)		

	@staticmethod
	def draw_line(screen, start_point, end_point, color):
		draw.line(screen, color, (start_point.x, start_point.y), (end_point.x, end_point.y), 2)

# ===================================================
# EXAMPLE

if __name__ == '__main__':
	from pygame import display
	from time import clock
	from vector import Vector 

	width = 800
	height = 600
	BLACK = (0, 0, 0)
	screen = display.set_mode((width, height))
	screen.fill(BLACK)

	current_time = clock()
	dt = 0

	while True:
		screen.fill(BLACK)
		dt = clock() - current_time
		current_time += dt

		DebugDrawings.draw_circle(screen, Vector(400, 300), 50, (255, 0, 0))
		DebugDrawings.draw_circle(screen, Vector(350, 250), 20, (0, 0, 255))
		DebugDrawings.draw_circle(screen, Vector(450, 250), 20, (0, 0, 255))
		DebugDrawings.draw_circle(screen, Vector(400, 370), 10, (0, 0, 255))
		DebugDrawings.draw_rect(screen, Vector(400, 300), 200, 200, (0, 255, 0))

		DebugDrawings.draw_line(screen, Vector(0, 0), Vector(800, 600), (255, 255, 0))

		display.flip()