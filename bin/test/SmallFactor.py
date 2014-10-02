from Test import Test
from sqlalchemy import select
from db import metadata
import db
import gmpy as gmp
from gmpy import mpz


class SmallFactor(Test):
			
	def run(self, key, testRun, keyReference, client, makePerm=True):
		res = gmp.gcd(self.product % key.n, key.n)
		
		if res == 1:
			status = 1
			outputText = 'No small prime factor up to ' + str(self.parameter) + ' found. '
		else:
			status = -2
			outputText = 'At least one small prime factor was found. '
		
		return status, outputText, []

	def __init__(self, engine=None, parameter=10000, shared=None):		
		super(SmallFactor,self).__init__(engine, parameter, shared)
		
		connection = self.engine.connect()
		s = select([db.smallFactorTable.c.product]).where(db.smallFactorTable.c.up_to==self.parameter)
		res = connection.execute(s).first()
		
		if res is None:
			n = 2
			self.product = mpz('1')		
			while n < self.parameter:
				self.product = self.product * n
				n = gmp.next_prime(n)
			connection.execute(db.smallFactorTable.insert(), up_to=self.parameter, 
				product = str(self.product))
		else:
			self.product = mpz(res[0])
				