import importlib
from sqlalchemy import select
import logging
from datetime import datetime
from key.RSA import RSA

import db
from test.Test import Test


class Tester(object):

	
	def __init__(self, testSet, engine, shared):
		self.testSet = testSet
		self.shared = shared
		self.engine = engine
		
		self.__syncTests = []
		self.__asyncTests = []
		self.__globalTests = []
		self.__syncDone = False

		connection = self.engine.connect()
		#load test_set config

		s = select([db.testSetTable]).where(db.testSetTable.c.id == self.testSet)

		if connection.execute(s).first() is None:
			connection.close()
			raise Exception('Invalid test set config: No test set with name ' + str(self.testSet) + ' defined.')
			
		#load test config
		s = select([db.testTable]).where(db.testTable.c.test_set == self.testSet)
		result=connection.execute(s)
		if result.first() is None:
			result.close()
			connection.close()
			raise Exception('Invalid test set config: Test set does not contain any test.')
		
		result=connection.execute(s)
		for row in result:
			i = importlib.import_module('test.' + row['name'])
			classname = getattr(i, row['name'])
			if not (issubclass(classname, Test)):
				result.close()
				connection.close()
				raise Exception('Invalid test set config: Test set does not contain any test.')
			
			temp = classname(self.engine, row['parameter'], self.shared)

			if row['type']==0:
				self.__syncTests.append(temp)
			if row['type']==1:
				self.__asyncTests.append(temp)
			if row['type']==2:
				self.__globalTests.append(temp)
				
		result.close()
		connection.close()
		
	def release(self):
		def releaseTests(tests):
			if tests is not None:
				for t in tests:
					t.release()
		releaseTests(self.__syncTests)
		releaseTests(self.__asyncTests)
		releaseTests(self.__globalTests)
			
	
	def testSync(self, keyType, keyFormat, key, keyReference, client, makePerm=True):
		self.keyType = keyType
		self.keyFormat = keyFormat
		self.key = key
		self.keyReference = keyReference
		self.client = client
		self.makePerm = makePerm
		self.started = datetime.now()
		
		connection = self.engine.connect()

		result=connection.execute(db.testRunTable.insert(), key_reference=self.keyReference, 
			client = self.client, key_type=self.keyType, key_format=self.keyFormat, 
			test_set=self.testSet, started=self.started)
			
		self.testRunId = result.inserted_primary_key[0]
		result.close()
		connection.close()

		self.__runTests(self.__syncTests)
		self.__syncDone=True
		if not self.__asyncTests and not self.__globalTests:
			self.__testsDone()
	
		return self.testRunId
	
	def testAsync(self, release=False): 
		if self.__syncDone:
			self.__runTests(self.__asyncTests)
			self.__runGlobalTests()
			self.__testsDone()
		if release:
			self.release()
		return self.testRunId
		
	def __testsDone(self):
		self.completed = datetime.now()
		
		connection = self.engine.connect()
		stmt = db.testRunTable.update().where(db.testRunTable.c.id == self.testRunId).\
			values(completed=self.completed)
		connection.execute(stmt)
		connection.close()
		self.__syncDone=False
		
	def __runTests(self, testCollection):
		connection = self.engine.connect()
		
		for t in testCollection:
			status, outputText, revoke = t.run(self.key, self.testRunId, self.keyReference, 
				self.client, self.makePerm)
			testName=t.__class__.__name__
			connection.execute(db.testResultTable.insert(), test_run=self.testRunId, 
				status=status, output=outputText, test=testName)
			
			if len(revoke)>0:
				logging.error('Currently tested key with test run ID: ' + str(self.testRunId) + 
					' compromises older keys according to results of test ' + testName + '. See results for details. ')
				for r in revoke:
					connection.execute(db.revokeKeysTable.insert(), test_run=self.testRunId, test=testName, revoke_key=r) 
		connection.close()
		
	def __runGlobalTests(self):
		connection = self.engine.connect()
		keys = []
		keyReferences = []
		
		s = select([db.keyStorageTable.c.modulus, db.keyStorageTable.c.exponent, db.keyStorageTable.c.test_run])
		result = connection.execute(s)		
		for row in result:
			k = RSA()
			k.modulus = row[0]
			k.exponent = row[1]
			keys.append(k)
			keyReferences.append(row[2])
			
		
		for t in self.__globalTests:
			status, outputText, revoke = t.run(keys, self.testRunId, keyReferences, 
				self.client, self.makePerm)
			testName=t.__class__.__name__
			connection.execute(db.testResultTable.insert(), test_run=self.testRunId, 
				status=status, output=outputText, test=testName)
			
			if len(revoke)>0:
				logging.error('Currently tested key with test run ID: ' + str(self.testRunId) + 
					' compromises older keys according to results of test ' + testName + '. See results for details. ')
				for r in revoke:
					connection.execute(db.revokeKeysTable.insert(), test_run=self.testRunId, test=testName, revoke_key=r) 
		
		
		connection.close()
		
		
def getTestSet(engine, client):
	connection = engine.connect()
	s = select ([db.clientTable.c.test_set]).where(db.clientTable.c.name==client)
	res = connection.execute(s).first()
	if res is None:
		connection.close()
		return None
	else:
		connection.close()		
		return res[0]
	
def initAllTests(engine, shared):
	connection = engine.connect()
	s = select([db.testSetTable.c.id])
	for r in connection.execute(s):
		tester = Tester(r[0], engine, shared)
	connection.close()
	