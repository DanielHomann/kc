from Test import Test

class UnusualModuloLength(Test):
			
	def run(self, key, testRun, keyReference, client, makePerm=True):
		length=len(bin(key.n))-2
		
		if length % 1024 == 0:
			outputText='No unusual modulo length detected. '
			status = 1
		else:
			outputText='Unusual modulo length ' + str(length) + ' detected.'
			status = -1
		return status, outputText, []

	def __init__(self, engine=None, parameter=0, shared=None):
		super(UnusualModuloLength,self).__init__(engine, parameter, shared)
