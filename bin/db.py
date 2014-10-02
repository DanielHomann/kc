from sqlalchemy import *
from os.path import isfile
from configuration import config


metadata = None

clientTable = None
testTable = None
testSetTable = None
testRunTable = None
testResultTable = None
revokeKeysTable = None
keyStorageTable = None
smallFactorTable = None
commonGCDTable = None
usedTable = None


#Every process needs its own Engine
def getEngine():
	type = config.get('db','Type')
	database = config.get('db', 'Database')
	user = config.get('db', 'User')
	password = config.get('db', 'Password')
	host = config.get('db', 'Host')
	echo = config.getboolean('db', 'Echo')
	
	connectionString = type + '://' + user + ':' + password + '@' + host + '/' + database
	
	return create_engine(connectionString, echo=echo)

#To be called once at the beginning of a session
def initDB():
	global metadata
	metadata = MetaData()
	
	engine = getEngine()
	maxKeyLength = config.getint('db', 'MaxKeyLength')
	
	global clientTable
	global testTable
	global testSetTable
	global testRunTable
	global testResultTable
	global revokeKeysTable
	global usedTable
	global keyStorageTable
	global smallFactorTable
	global commonGCDTable
	
	clientTable = Table('Client', metadata,
		Column('name', String(40), primary_key=True),
		Column('test_set', None, ForeignKey('Test_Set.id')),
		Column('admin', Boolean, nullable=False, default=False),
	)		
	
	testTable = Table('Test', metadata,
		Column('name', String(20), primary_key=True),
		Column('test_set', None, ForeignKey('Test_Set.id'), primary_key=True),
		Column('type', Integer, default = 0, nullable=False),
		Column('parameter', Integer, default=0),
	)

	testSetTable = Table('Test_Set', metadata,
		Column('id', Integer, Sequence('Test_Set_id_seq'), primary_key=True),
		Column('description', String(400))
	)


	testRunTable = Table('Test_Run', metadata,
		Column('id', Integer, Sequence('Test_Run_id_seq'), primary_key=True),
		Column('key_reference', Integer),
		Column('client', None, ForeignKey('Client.name'), nullable = False),
		Column('key_type', String(20)),
		Column('key_format', String(20)),
		Column('test_set', None, ForeignKey('Test_Set.id')),
		Column('started', DateTime),
		Column('completed', DateTime),
	)
		
	testResultTable = Table('Test_Result', metadata, 
		Column('test_run', None, ForeignKey('Test_Run.id'), primary_key=True),
		Column('test', None, ForeignKey('Test.name'), primary_key=True),
		Column('status', Integer, nullable=False, default=0),
		Column('output', String(400)),
	)

	revokeKeysTable = Table('Revoke_Keys', metadata,
		Column('test_run', None, ForeignKey('Test_Run.id'), autoincrement=False, primary_key=True),
		Column('test', None, ForeignKey('Test.name'), autoincrement=False, primary_key=True),
		Column('revoke_key',  None, ForeignKey('Test_Run.id'), autoincrement=False, primary_key=True),
		)
		
	usedTable = Table('Used', metadata , 
		Column('hash', String(maxKeyLength)),
		Column('test', String(20), primary_key=True, autoincrement=False),
		Column('test_run', None, ForeignKey('Test_Run.id'), primary_key=True, autoincrement=False),
		Column('key_reference', Integer),
		Column('client', None, ForeignKey('Client.name')),
		)
		
	keyStorageTable = Table('Key_Storage', metadata , 
		Column('test_run', None, ForeignKey('Test_Run.id'), primary_key=True, autoincrement=False),
		Column('client', None, ForeignKey('Client.name')),
		Column('key_reference', Integer),
		Column('modulus', String(maxKeyLength)),
		Column('exponent', Integer))
	
	smallFactorTable = Table('Small_Factor', metadata , 
		Column('up_to', BigInteger, primary_key=True, autoincrement=False),
		Column('product', Text(2**32-1)),
	)
	
	commonGCDTable = Table('Common_GCD', metadata , 
		Column('product', Text(2**32-1)),
		Column('id', Integer, Sequence('Common_GCD_id_seq'), primary_key=True)
	)
		
	metadata.create_all(engine)
	
		
#Only to be runned when Database is build
def createConfig():
	engine = getEngine()
	connection = engine.connect()
	
	connection.execute(testSetTable.insert(), [
		{'id': 1, 'description': 'Do only input work'},
		{'id': 2, 'description': 'Do all tests'},
		{'id': 3, 'description': 'Do global tests'},
	])
	
	connection.execute(testTable.insert(), [
		{'name': 'UsedModulo', 'test_set': 1, 'type': 0, 'parameter': 0},
		{'name': 'KeyStorage', 'test_set': 1, 'type': 0, 'parameter': 0},
		{'name': 'CommonGCDInput', 'test_set': 1, 'type': 0, 'parameter': 0},
		{'name': 'UsedModulo', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'UsedKey', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'KeyStorage', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'SmallFactor', 'test_set': 2, 'type': 0, 'parameter': 1000000},
		{'name': 'DebianWeakKey', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'UnusualExponent', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'UnusualModuloLength', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'CommonGCD', 'test_set': 2, 'type': 0, 'parameter': 0},
		{'name': 'FermatFactor', 'test_set': 2, 'type': 0, 'parameter': 10000000},
		{'name': 'GlobalCommonGCD', 'test_set': 3, 'type': 2, 'parameter': 0},
	])
	
	connection.execute(clientTable.insert(), [ 
		{'name': 'all', 'admin': True, 'test_set': 2},
		{'name': 'input', 'admin': True, 'test_set': 1},
		{'name': 'global', 'admin': True, 'test_set': 3},
	])
	
	connection.execute(commonGCDTable.insert(), [ 
		{'id': 1, 'product': '1'},
	])
	
	connection.close()
	
#Deletes whole database
def clearDB():
	global metadata
	engine = getEngine()
	metadata = MetaData(reflect=True, bind=engine)
	metadata.drop_all()
	for t in metadata.sorted_tables:
		metadata.remove(t)
	metadata = None

#Reset database to initial state
def resetDB():
	clearDB()
	initDB()
	createConfig()
	


