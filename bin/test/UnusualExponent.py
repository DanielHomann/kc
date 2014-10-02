from Test import Test

class UnusualExponent(Test):
			
	def run(self, key, testRun, keyReference, client, makePerm=True):
		if key.e==65537:
			outputText='No unusual exponent detected.'
			status = 1
		else:
			outputText='Unusual exponent ' + str(key.e) + ' detected.'
			status = -1
		return status, outputText, []

	def __init__(self, engine=None, parameter=0, shared=None):
		super(UnusualExponent,self).__init__(engine, parameter, shared)
