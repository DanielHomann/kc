from Key import Key
class RSA(Key):
	def __init__(self, n=0, e=0):
		self.n=n
		self.e=e
		
	def __str__(self):
		return 'RSA key: modulus = ' + str(self.n) + ', exponent = ' + str(self.e)
		
	def __hash__(self):
		return hash((self.n, self.e))
		
	def __eq__(self, other):
		return other and self.n == other.n and self.e == other.e
		
def modulo(key):
	return hash(key.n)
	
	