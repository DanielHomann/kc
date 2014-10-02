from optparse import OptionParser  
import os.path
from os.path import isfile, isdir
from os import listdir
from sqlalchemy import select
import logging

from db import resetDB, initDB, getEngine
import db
from Result import Result, hasAccess
from Parser import getParam, parse, hasParser
from Tester import Tester, getTestSet, initAllTests
from configuration import config, getShared
from ExitPool import ExitPool


shared = None
engine = None
tester = None
client = None
makePerm = None
verbose = None

def initWorker(testSet, Client, MakePerm, Verbose, Shared):
	global engine
	global tester
	global shared
	global client
	global makePerm
	global verbose
	
	engine = getEngine()
	shared = Shared	
	client = Client
	makePerm = MakePerm
	verbose = Verbose
	
	tester = Tester(testSet, engine, shared)
	
def exitWorker():
	tester.release()

	
def test(filenames):
	f,i = filenames
	
	try:
		with open(f) as file:
			string = file.read()
	except:
		return 'Could not open file: ' + f
				
	keyFormat, keyType = getParam(string)
	if keyFormat is None or keyType is None:
		return 'Unknown key format in file: ' + f
				
	if hasParser(string):
		key = parse(string)
	else:
		return 'Input in file: ' + f + ' has key format: ' + keyFormat + ' and key type: ' + keyType + '. There is no parser for this format. '
				
	if key is None:
		return 'Could not extract key from file: ' + f
		
	return doTest(tester, keyType, keyFormat, key, i, client, makePerm, verbose, engine)

		
def doTest(tester, keyType, keyFormat, key, keyReference, client, makePerm, verbose, engine):
	id = tester.testSync(keyType, keyFormat, key, keyReference , client, makePerm)
	tester.testAsync()

	if verbose:
		return Result(engine, id , client).getAll()
	else:
		result = Result(engine, id, client).testRun()
		return 'Input successful. Test Run ID: ' + str(result)

if __name__ == '__main__':	
	#Handle input parameters
	use = 'Usage: %prog [options] -c <Client> -t <Test Set> -k <Key Reference> -p -b -q -f <Filename> -r <Test Run ID>' 
	vers="%prog 0.1"
	parser = OptionParser(usage = use, version = vers)

	parser.add_option("-c", "--client", dest="client", help="Input client name.")
	parser.add_option("-t", "--testset", dest="testSet", help="Input test set to be run.") 
	parser.add_option("-p", "--nonpermanent", action="store_false", dest="makePerm", 
		default=True, help="Prevent results of test to affect future test runs.")
	parser.add_option("-k", "--keyreference", dest="keyReference", help="Input the key reference. ") 
	parser.add_option("-f", "--file", dest="file", 
		help="File containing the key, which should be tested", metavar="FILE")
	parser.add_option("-r", "--result", dest="result", help="Display results of past test run. ")
	parser.add_option("-q", "--quiet", action="store_false", dest="verbose", 
		default=True, help="Run application quiet. ")
	parser.add_option("-b", "--batch", action="store_true", dest="batch", default=False, 
		help="Batch import multiple keys. File name is used as key reference")
	parser.add_option("-g", "--global", action="store_true", dest="globalTest", default=False, 
		help="Execute global tests")
	parser.add_option("--reset", action="store_true", dest="reset", 
		default=False, help="Deletes all database content and restores initial setup.")

	options, args = parser.parse_args()
	
	#Mutually exclusive options
	if options.client and options.testSet:
		parser.error("options --client and --testset are mutually exclusive.")
		
	if options.testSet and options.result:
		parser.error("options --testset and --result are mutually exclusive.")
		
	if options.file and options.result:
		parser.error("options --file and --result are mutually exclusive. ")

	if options.batch and options.result:
		parser.error("options --batch and --result are mutually exclusive. ")
		
	if options.batch and options.keyReference:
		parser.error("options --batch and --keyReference are mutually exclusive. The key reference will be determined by the file name.")
		
	if options.globalTest and options.keyReference: 
		parser.error("options --global and --keyreference are mutually exclusive. ")
		
	if options.globalTest and options.batch:
		parser.error("options --global and --batch are mutually exclusive. ")
	
	if options.globalTest and options.result:
		parser.error("options --global and --result are mutually exclusive. ")
		
	if options.globalTest and options.file:
		parser.error("options --global and --file are mutually exclusive. ")
		
	#Enough options specified?	
	if not(options.result or options.file or options.reset or options.globalTest):
		parser.error("Not enough options specified")
		
	if options.file or options.globalTest:
		if not(options.testSet or options.client):
			parser.error("An test or an client has to be specified")
			
		if not(options.keyReference or options.batch or options.globalTest):
			parser.error("You have to either specify batch mode, globalTest or give an keyReference")
		
	#Loading data to test input validity
	initDB()
	engine=getEngine()
	
	if options.client:
		client = options.client
	else:
		client = 'admin'
		
	if options.testSet:
		testSet = options.testSet

	#Is input valid
	if options.keyReference:
		try:
			options.keyReference = int(options.keyReference)
		except:
			parser.error("Specified Key Reference is no int")

	if options.file:
		if options.batch:
			if not isdir(options.file):
				parser.error("In batch mode their has to specified a valid directory")
			#add trailing slash
			options.file = os.path.join(options.file, '')
		else:
			if not isfile(options.file):
				parser.error("Specified file does not exist")

	if options.batch:
		for f in listdir(options.file):
			try:
				int(f)
			except:
				parser.error('Filename ' + f + ' can not be converted to int')
				
			
	connection = engine.connect()
	if options.client:
		testSet = getTestSet(engine, options.client)
		if testSet is None:
			connection.close()
			parser.error("Client name does not exist or has no test set assigned. ")
		
	if options.testSet:
		table = getTable(testSetTable, connection)
		s = select ([table]).where(table.c.id==options.testSet)
		if connection.execute(s).first() is None:
			connection.close()
			parser.error("Test set does not exist")
			
	if options.result:
		if not hasAccess(engine, options.result, client):
			connection.close()
			parser.error("Test Run id does not exist or does not belong to the specified client")
	connection.close()

	if options.file:
		filenames=[]
		
		if options.batch:
			filenames = [[options.file+f, int(f)] for f in listdir(options.file)]
		else:
			filenames = [[options.file, options.keyReference]]

	shared = getShared()
	
	#start executing the user commands
	if options.reset:
		resetDB()
		initAllTests(engine, shared)
		exit()

	if options.result:
		result = Result(engine, options.result, client)
		print result.getAll()
		exit()
	
	if options.file:
		cores = min(config.getint('keycheck', 'NumberCores'), len(filenames))	
		pool = ExitPool(cores, initWorker, [testSet, client, options.makePerm, options.verbose, shared], exitWorker)
		result=pool.map(test, filenames, chunksize=1)	
		pool.close()
		pool.join()
		
	
	if options.globalTest:
		tester = Tester(testSet, engine, shared)
		result=[doTest(tester, None, None, None, None, client, options.makePerm, options.verbose, engine)]
		tester.release()
		
	for s in result:
		print s
			



	

