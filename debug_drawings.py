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