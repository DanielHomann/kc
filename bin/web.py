from flask import Flask, request, abort
import logging
#from multiprocessing import Pool
import threading

from Result import Result, hasAccess
from Parser import getParam, parse, hasParser
from Tester import Tester, getTestSet
from configuration import config, getShared
from db import getEngine, initDB



app = Flask(__name__)
shared = None
#syncPool = None
#asyncPool = None

@app.route('/', methods=['POST'])
def doTest():
	# to load this data I need a certificate,
	#therefore at the moment no validation
	client = 'all'
	logging.debug(request)
	f = request.files['key']
	
	string = f.read()
	logging.debug(string)
	
	keyReference = request.form['keyreference']
	logging.debug(keyReference)
	
	engine = getEngine()
	testSet = getTestSet(engine, client)
	if testSet is None:
		logging.info('client ' + client + ' does not exist or has no test set assigned. ')
		abort(400)
	
	try:
		keyReference = int(keyReference)
	except:
		#Http code 400: Bad request
		logging.info('keyReference: ' + keyReference + ' is no integer.')
		abort(400)
	
	if not hasParser(string):
		logging.info('No valid input. ')
		logging.info(string)
		abort(400)
	
	key = parse(string)
	if key is None:
		logging.info('No valid input. ')
		logging.info(string)
		abort(400)	

	keyFormat, keyType = getParam(string)
	if keyFormat is None or keyType is None:
		logging.info('keyFormat: ' + keyFormat + ' and keyType: ' + keyType +' are not valid')
		abort(400)
	
	tester = Tester(testSet, engine, shared)
	id=tester.testSync(keyType, keyFormat, key, keyReference, client)
	threading.Thread(target=tester.testAsync, args=[True]).start()
	#asyncPool.apply_async(testAsync, tester)
	#asyncPool.apply_async(tester.testAsync, [True])
	#apply(tester.testAsync, [True])

	res = Result(engine, id,client).getJSON()
	return res;
	
	
def testAsync(tester):
	print 'testAsync'
	tester.testAsync(True)
	tester.release()
	

@app.route('/<int:testRunId>/', methods=['GET'])
def result(testRunId):
	# to load this data I need a certificate,
	#therefore at the moment no validation
	client = 'all'
	
	try:
		testRunId = int(testRunId)
	except:
		logging.info(str(testRunId) + ' is no valid test run ID. ')
		abort(400)
	
	engine = getEngine()
	
	if not hasAccess(engine, testRunId, client):
		#Http code 403: Forbidden
		logging.warning('Unauthorized access tried by ' + client + ' on Test run ID ' + str(testRunId))
		abort(403)
	
	res = Result(engine, testRunId, client).getJSON()
	return res;
	
	
if __name__ == '__main__':
	global syncPool
	global asyncPool
	
	app.debug = config.getboolean('web', 'Debug')
	#app.logger.setLevel(logging.WARNING)
	initDB()
	shared = getShared()
	
	#asyncCores = config.getint('web', 'NumberCoresAsync')
	#:asyncPool = Pool(asyncCores)
	
	app.run()