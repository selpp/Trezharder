# Screen Reader
from pygame import image, surfarray

# ===================================================
# SCREENREADER

class ScreenReader(object):
	@staticmethod
	def screen_to_array(screen, width, height):
		string_image = image.tostring(screen, 'RGB')
		surf = image.fromstring(string_image, (width, height), 'RGB')
		arr = surfarray.array3d(surf)
		return arr
