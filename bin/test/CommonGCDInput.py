import gmpy as gmp
from gmpy import mpz
from sqlalchemy import select

from Test import Test
import db


class CommonGCDInput(Test):
	
	def run(self, key, testRun, keyReference, client, makePerm=True):		
		status = 1
		
		if makePerm:
			n = mpz(key.n)
			outputText = 'Modulo added to Common GCD database'
			self.product *= n	
		else:
			outputText = 'You choosed not to add the modulo to the database'
			
		return status, outputText, []
	
	def __init__(self, engine, parameter=0, shared=None):
		super(CommonGCDInput,self).__init__(engine, parameter, shared)
		
		self.lock = shared["CommonGCD"]
		self.product = mpz(1)

		
	def release(self):
		with self.lock:
			connection = self.engine.connect()
			s = select([db.commonGCDTable.c.product])
			res=connection.execute(s).first()
			if not res is None:
				temp = mpz(res[0])
			else:
				temp = mpz(1)
			lcm = gmp.lcm(temp, self.product)
			s=db.commonGCDTable.update().where(db.commonGCDTable.c.id==1).values(product=str(lcm))
			connection.execute(s)
			connection.close()
		
		
		
		