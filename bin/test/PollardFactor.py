from Test import Test
import gmpy as gmp
from gmpy import mpz

class PollardFactor(Test):		
	def run(self, key, testRun, keyReference, client, makePerm=True):
		res = extFactor(key.n, self.parameter)
		if res:
			status = -2
			outputText = 'A prime factor was found. '
		else:
			status = 1
			outputText = 'No nearly equal factors with maximal difference ' + str(2*self.parameter) + ' found. '
		return status, outputText, []

	def __init__(self, engine=None, parameter=0, shared=None):
		super(PollardFactor,self).__init__(engine, parameter, shared)		

