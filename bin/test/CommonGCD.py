import gmpy as gmp
from gmpy import mpz
from sqlalchemy import select

from Test import Test
import db


class CommonGCD(Test):
	def run(self, key, testRun, keyReference, client, makePerm=True):
		
		n = mpz(key.n)
		res = gmp.gcd(self.namespace.prod % n, n)
				
		if res == 1:
			status = 1
			outputText = 'No common GCD with the already tested keys found. '			
		else:
			status = -2
			outputText = 'At least one common factor with an already tested key found. '
		
		if makePerm:
			with self.lock:
				self.namespace.prod *= n	
		
		return status, outputText, []
	
	
	
	def __init__(self, engine, parameter=0, shared=None):
		super(CommonGCD,self).__init__(engine, parameter, shared)
		
		self.lock = shared["CommonGCD"]
		self.namespace = shared["Namespace"]
		
		with self.lock:
			self.namespace.gcdProcesses += 1
			if self.namespace.gcdProcesses == 1:
				connection = self.engine.connect()
				s = select([db.commonGCDTable.c.product])
				res = connection.execute(s).first()

				if res is None:
					self.namespace.prod = mpz(1)
				else:
					self.namespace.prod = mpz(res[0])
					
				connection.close()
	
	def release(self):
		with self.lock:
			self.namespace.gcdProcesses -= 1
			if self.namespace.gcdProcesses == 0:
				connection = self.engine.connect()
				s=db.commonGCDTable.update().where(db.commonGCDTable.c.id==1).values(product=str(self.namespace.prod))
				connection.execute(s)
				connection.close()

		