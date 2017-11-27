# Vector utils
from math import sqrt

# ===================================================
# VECTOR

class Vector(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __add__(self, other):
		return Vector(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return Vector(self.x - other.x, self.y - other.y)

	def __abs__(self):
		return Vector(abs(self.x), abs(self.y))

	def __mul__(self, other):
		return  Vector(self.x * other, self.y * other) if type(other) == float or type(other) == int else Vector(self.x * other.x, self.y * other.y)

	def __div__(self, other):
		if (type(other) == int or type(other) == float) and other == 0:
			raise NameError('Division by zero')
		if type(other) == Vector and (other.x == 0 or other.y == 0):
			raise NameError('Division by zero')
		return  Vector(self.x / other, self.y / other) if type(other) == float or type(other) == int else Vector(self.x / other.x, self.y / other.y)

	def dot(self, other):
		return self.x * other.x + self.y * other.y

	def __pow__(self, power):
		return Vector(self.x**power, self.y**power)

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def distance(self, other):
		return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

	def normalized(self):
		n = sqrt(self.x**2 + self.y**2)
		if n == 0:
			return self
		return self / n

	def magnitude(self):
		return sqrt(self.x**2 + self.y**2)

	def __str__(self):
		return '(' + str(self.x) + ', ' + str(self.y) + ')'

# ===================================================
# EXAMPLE: Point an operations

if __name__ == '__main__':
	origin = Vector(0, 0)
	print 'origin: ' + str(origin)
	
	p1 = origin + Vector(1, 0)
	print 'p1: (x: +1, y: 0) ' + str(p1)

	p1 = p1 - Vector(2, 0)
	print 'p1: (x: -2, y: 0) ' + str(p1)

	p1 = p1 * Vector(2, 0)
	print 'p1: (x: *2, y: 0) ' + str(p1)

	p1 = p1 / Vector(1, 1)
	print 'p1: (x: /1, y: 0) ' + str(p1)

	p1 = p1**2
	print 'p1: (x: **2, y: **2) ' + str(p1)

	p1 = abs(p1)
	print 'p1: (x: abs, y: abs) ' + str(p1)

	b = p1 == Vector(1, 1)
	print 'p1: ==(1, 1) ' + str(b)

	d = Vector(1, 2).distance(Vector(2, 1))
	print 'd: (1, 2) (2, 1) ' + str(d)
	
	print 'p1: norm ' + str(p1) + '-> ' + str(p1.normalized())	

	p2 = Vector(1, 2)
	print 'p2: scalar mul: (1, 2) * 2.0 -> ' + str(p2 * 2.0)
	print 'p2: scalar mul: (1, 2) / 2.0 -> ' + str(p2 / 2.0)

	p3 = Vector(2, 3)
	print 'p3: (2, 3) magnitude: ' + str(p3.magnitude())
