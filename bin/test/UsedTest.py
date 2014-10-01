from sqlalchemy import select, and_, not_
import logging

from Test import Test
import db
from configuration import config


maxKeyLength = config.getint('db', 'MaxKeyLength')

class UsedTest(Test):
			
	def run(self, key, testRun, keyReference, client, makePerm=True):
		
		comp = self.comparator(key)
		lenComp = len(str(comp))
		if  lenComp > maxKeyLength:
			outputText='The ' + self.compare + ' which should be tested is ' + lenComp + ' bit long, this is too long for UsedModulo. Increase MaxKeyLength.'
			logging.warning(outputText)
			status = 0
			return status, outputText, []
			
		connection=self.engine.connect()
		s = select([db.usedTable.c.hash]).where(and_(db.usedTable.c.hash == comp, db.usedTable.c.test == self.test))

		if connection.execute(s).first() is None:
			status =1
			outputText = 'The ' + self.compare + ' has not been used before.'
			revokeKeyReference=[]		
		else:
			s = select([db.usedTable.c.test_run]).where(
			and_(db.usedTable.c.hash == comp,
			db.usedTable.c.test == self.test,
				not_(and_(db.usedTable.c.key_reference == keyReference, 
					db.usedTable.c.client == client
					))
				)
			)
			
			if connection.execute(s).first() is None:
				status=1
				outputText = 'The ' + self.compare + ' has not been used used twice, but the same key (same key reference and client) has been tested before.'
				revokeKeyReference=[]
				
			else:
				status =-2
				outputText = 'The ' + self.compare + ' has been used before. For own prior usages see revokeKeyReference.'
				s = select([db.usedTable.c.test_run]).where(and_(db.usedTable.c.hash == comp, db.usedTable.c.test == self.test))	
				result = connection.execute(s)
				revokeKeyReference = [r for r, in result]
				result.close()
			
		if makePerm:
			connection.execute(db.usedTable.insert(), hash=comp, test_run=testRun, test = self.test, 
				key_reference=keyReference, client=client)
		connection.close()
		return status, outputText, revokeKeyReference
		
	def __init__(self, engine, parameter=0, shared = None):
		super(UsedTest,self).__init__(engine, parameter, shared)
		
		
	