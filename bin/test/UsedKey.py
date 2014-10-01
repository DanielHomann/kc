from UsedTest import UsedTest

class UsedKey(UsedTest):
	def __init__(self, engine, parameter=0, shared = None):
		super(UsedKey,self).__init__(engine, parameter, shared)
		
		self.comparator = hash
		self.compare = 'key'
		self.test = 'UsedKey'
		
		
	
		