class Key(object):
	def __str__(self):
		raise NotImplementedError
		
	def __hash__(self):
		raise NotImplementedError
		
	def __eq__(self, other):
		raise NotImplementedError