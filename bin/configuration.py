from ConfigParser import SafeConfigParser
import logging
import logging.handlers
from multiprocessing import Manager
from gmpy import mpz

config = SafeConfigParser()
config.read('config.cfg')

def addLogger(logger):
	logger.addHandler(fileHandler)
	#Ggf. Anschalten
	#logger.addHandler(syslogHandler)

	
fileHandler = logging.FileHandler(config.get('configuration', 'LogFile'))
fileHandler.setLevel(config.getint('configuration', 'FileLoggingLevel'))
fileHandler.setFormatter(logging.Formatter(
	'%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(funcName)s:%(lineno)d]'
))


syslogHandler = logging.handlers.SysLogHandler()
syslogHandler.setLevel(config.getint('configuration', 'SyslogLoggingLevel'))

loggers = []

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
addLogger(logger)

logger=logging.getLogger('werkzeug')
logger.setLevel(logging.WARNING)
addLogger(logger)

logging.debug('Logger has started.')


def getShared():
	manager = Manager()
	namespace = manager.Namespace()
	namespace.prod = mpz(1)
	namespace.gcdProcesses = 0
	lockGCD = manager.RLock()
	lockExtGCD = manager.RLock()
	shared = {"Namespace": namespace, "CommonGCD": lockGCD, "ExtCommonGCD": lockExtGCD}
	return shared