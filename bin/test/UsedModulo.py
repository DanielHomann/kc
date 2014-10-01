from UsedTest import UsedTest
import key.RSA

class UsedModulo(UsedTest):
		
	def __init__(self, engine, parameter=0, shared = None):
		super(UsedModulo,self).__init__(engine, parameter, shared)
		
		self.comparator = key.RSA.modulo
		self.compare = 'modulo'
		self.test = 'UsedModulo'
		
		
	