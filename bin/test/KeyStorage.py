from Test import Test
import db
from configuration import config

_maxKeyLength = config.getint('db', 'MaxKeyLength')

class KeyStorage(Test):
			
	def run(self, key, testRun, keyReference, client, makePerm=True):
	
		if makePerm:
			if len(str(key.n))>_maxKeyLength:
				outputText='The key which should be logged is ' + str(len(bin(key.n))-2) + ' bit long, this is too long for KeyStorage. Increase MaxKeyLength.'
				logging.warning(outputText)
				status = 0
			else:			
				connection=self.engine.connect()
				connection.execute(db.keyStorageTable.insert(), modulus=str(key.n), test_run=testRun,
					key_reference=keyReference, client=client, exponent=key.e)
				connection.close()
				outputText='The key has been logged. '
				status = 1
		return status, outputText, []
		
	def __init__(self, engine=None, parameter=0, shared=None):
		super(KeyStorage,self).__init__(engine, parameter, shared)
		
		
