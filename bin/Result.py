from sqlalchemy import select, func, and_
from xml.etree.ElementTree import Element, SubElement, tostring
import json
import logging

import db
from db import getEngine
from configuration import config

version = "1.0"
#If a test warns, does this mean that the Key is bad
WarningBadKey=config.getboolean('Result', 'WarningBadKey')

def hasAccess(engine, id, client):
	connection = engine.connect()
		
	if isAdmin(engine, client):
		s=select([db.testRunTable.c.id]).where(db.testRunTable.c.id==id)
	else:
		s=select([db.testRunTable.c.id]).where(and_(db.testRunTable.c.id==id, db.testRunTable.c.client==client))
		
	result = not (connection.execute(s).first() is None)
	connection.close()
	return result
		
	
def isAdmin(engine, client):
	connection=engine.connect()
		
	s=select([db.clientTable.c.admin]).where(db.clientTable.c.name == client)
	result = connection.execute(s).first()
		
	if result is None:
		connection.close()
		return False
	else:		
		connection.close()
		return result[0]

def testStatus(status):
	if status==1:
		return "Passed"
	if status==0:
		return "Not Applicable"
	if status==-1:
		if WarningBadKey:
			return "WARNING"
		else:
			return "Warning"
	if status==-2:
		return "FAILED"
	return "Unknown"

class Result(object):
	def __init__(self, engine, id, client):
		self.__id = id
		self.__client = client
		self.engine = engine
		self.update()
		
	def set(self, id, client):
		if not id is None:
			self.__id = id
		if not client is None:
			self.__client = client
		self.update()
		
		
	def update(self):
		if not hasAccess(self.engine, self.__id, self.__client):
			raise Exception('Test_Run.id ' + str(self.__id) + 
				' does not exist or does not belong to client ' + self.__client + '. ')
		
		connection=self.engine.connect()
		
		self.__admin = isAdmin(self.engine, self.__client)
		
		if self.__admin:
			s=select([db.testRunTable]).where(db.testRunTable.c.id==self.__id)
		else:
			s=select([db.testRunTable]).where(and_(db.testRunTable.c.id==self.__id, 
				db.testRunTable.c.client==self.__client))
		
		result = connection.execute(s).first()
		
		self.__keyReference=result['key_reference']
		self.__started = result['started']
		self.__completed = result['completed']
		self.__testSet = result['test_set']
		self.__keyType = result['key_type']
		self.__keyFormat = result['key_format']
		
		self.__outputText=[]
		self.__testStatus=[]
		self.__testNames=[]
		s=select([db.testResultTable]).where(db.testResultTable.c.test_run==self.__id)
		result = connection.execute(s)
		for r in result:
			self.__outputText.append(r['output'])
			self.__testStatus.append(r['status'])
			self.__testNames.append(r['test'])
		result.close()
		
		self.__testsFailed=self.__testStatus.count(-2)
		self.__testsNotApplicable=self.__testStatus.count(0)
		self.__testsPassed=self.__testStatus.count(1)
		self.__testsWarning=self.__testStatus.count(-1)
		
		self.__tests = self.__testsFailed + self.__testsNotApplicable + self.__testsPassed + self.__testsWarning
		
		if self.__tests <> len(self.__testStatus):
			logging.error('Unknown test status encountered in result.')
			raise Exception('Unknown test status encountered in result.')
			
		
		self.__revokeKeys = []
		if self.__admin:
			s=select([db.testRunTable.c.client, db.testRunTable.c.key_reference]).where(and_(db.revokeKeysTable.c.test_run == self.__id,
				db.revokeKeysTable.c.revoke_key == db.testRunTable.c.id)).distinct()
		else:
			s=select([db.testRunTable.c.client, db.testRunTable.c.key_reference]).where(and_(db.revokeKeysTable.c.test_run == self.__id,
				db.revokeKeysTable.c.revoke_key == db.testRunTable.c.id, db.testRunTable.c.client == self.__client)).distinct()
				
		result = connection.execute(s)
		for r in result:
			self.__revokeKeys.append((r[0],r[1]))
			
		result.close()
		connection.close()
		
	def isGoodKey(self, update=False):
		if update:
			update()
			
		if WarningBadKey:
			return self.testsFailed()==0 and self.testsWarning()==0
		else:
			return self.testsFailed()==0
	
	def tests(self, update=False):
		if update:
			update()
		return self.__tests;
		
	def testsFailed(self, update=False):
		if update:
			update()
		return self.__testsFailed
		
	def testsWarning(self, update=False):
		if update:
			update()
		return self.__testsWarning
	
	def testsPassed(self, update=False):
		if update:
			update()
		return self.__testsPassed;
	
	def testsNotApplicable(self, update=False):
		if update:
			update()
		return self.__testsNotApplicable
	
	def testsPending(self, update=False):
		if update:
			update()
		return self.tests()-self.testsPassed()-self.testsFailed()-self.testsNotApplicable()-self.testsWarning()
	
	def started(self, update=False):
		if update:
			update()
		return self.__started
	
	def completed(self, update=False):
		return not(self.__completed is None)
	
	def runtime(self, update=False):
		if update:
			self.update()
		return self.__completed-self.__started
		

	
	def outputText(self, update=False):
		if update:
			update()
		
		temp = zip(self.__testStatus, self.__outputText, self.__testNames)
		l = []
		for status, text, name in sorted(temp, key=lambda temp: temp[0]):
			l.append(testStatus(status) + ' ' + name + ': ' + text)
		return l
	
	def testRun(self):
		return self.__id
	
	def keyReference(self):
		return self.__keyReference
	
	def client(self):
		return self.__client
		
	def keyType(self):
		return self.__keyType
		
	def keyFormat(self):
		return self.__keyFormat
	
	def revokeKeyReference(self, update=False):
		if update:
			update()
		l = []
		for client, keyReference in self.__revokeKeys:
			l.append('client: ' + client + '\t\tkey reference: ' + str(keyReference))
		return l
		
	def getAll(self, update=False):
		if update:
			update()
		s='-------------------------------------------------------\n'
		s += 'Results of Test Run: ' + str(self.testRun()) +'\n'
		s += 'Key Reference: ' + str(self.keyReference()) +'\n'
		s += 'Key Type: ' + str(self.keyType()) + '\n'
		s += 'Key Format: ' + str(self.keyFormat()) + '\n'
		s+= 'Client: ' + self.client() + '\n'
		s+= 'Test run started at: ' + str(self.started()) + '\n'
		if self.completed():
			s+= 'Test run completed with runtime: ' + str(self.runtime()) + '\n'
		else:
			s+= 'Test not yet completed. '
		s+='\n'
		s+= 'Total number of tests: ' + str(self.tests()) + '\n'
		s+= '	Passed: ' + str(self.testsPassed()) + '\n'
		s+= '	Not applicable: ' + str(self.testsNotApplicable()) + '\n'
		s+= '	Warning: ' + str(self.testsWarning()) + '\n'
		s+= '	Failed: ' + str(self.testsFailed()) + '\n'
		s+= '	Still Pending: ' + str(self.testsPending()) + '\n'
		s+= '\n'
		if self.isGoodKey():
			s+='The key appear to be a good key. No vulnerabilities were found.'
		else:
			s+='The key has at least one known vulnerability. Do not use it.'
		s+='\n\n'
		s+='Detailed Test Output: \n'
		for o in self.outputText():
			s+=o+'\n'
			
		if len(self.revokeKeyReference())>0:
			s+='\nDue to the results you should revoke the following keys:\n'
			for r in self.revokeKeyReference():
				s+=str(r)+'\n'
		s+='-------------------------------------------------------\n'
		
		return s
	
	def getDict(self, update=False):
		if update:
			update()
			
		overview = dict([
			('number of tests', self.tests()),
			('passed tests', self.testsPassed()),
			('not applicable tests', self.testsNotApplicable()),
			('warning tests', self.testsWarning()),
			('failed tests', self.testsFailed()),
			('still pending tests', self.testsPending())
			])
		
		tests = {}
		for status, text, name in zip(self.__testStatus, self.__outputText, self.__testNames):
			test =dict([
				('status', status),
				('text', text)
				])
			tests[name] = test
		
		revokes = []
		for client, keyReference in self.__revokeKeys:
			revoke = dict([
				('client', client),
				('key reference', keyReference)
				])
			revokes.append(revoke)
			
		root = dict([('version', version),
			('test run', self.testRun()),
			('key reference', self.keyReference()),
			('key type', self.keyType()),
			('key format', self.keyFormat()),
			('client', self.client()),
			('started', str(self.started())),
			('completed', self.completed()),
			('is good key', self.isGoodKey()),
			('test overview', overview),
			('tests', tests),
			('revokes', revokes)
		])	
		if self.completed():
			root['runtime']=str(self.runtime())
		
		return root
		
	def getJSON(self, update=False, indent=None, sort_keys=False):
		dict = self.getDict(update)
		res = json.dumps(dict, indent=indent, sort_keys=sort_keys)
		return res
		
	def getXML(self, update=False):	
		def XML(root, input):
			if type(input) is dict:
				for key, value in input.items():
					elem = SubElement(root, str(key))
					XML(elem, value)
				return
			if type(input) is list:
				key = 1
				for value in input:
					elem = SubElement(root, str(key))
					XML(elem,value)
					key+=1
				return
			root.text=str(input)
			
		data = self.getDict(update)
		root = Element('result')
		XML(root, data)
		return tostring(root)
		