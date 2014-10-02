from subprocess import Popen,PIPE
from Test import Test

class DebianWeakKey(Test):
			
	def run(self, key, testRun, keyReference, client, makePerm=True):
		
		length = len(bin(key.n))-2
		if length not in [512, 1024, 2048, 4096]:
			status = 0
			outputText = 'Non-Standard key length. Test is not applicable. '
			return status, outputText, []
		
				
		k = hex(key.n)[2:-1].upper()
		ossl = Popen(['openssl-vulnkey', 'tests/debian/1', '-b', str(length), '-m', k], stdout=PIPE, stderr=PIPE) #']
		(stdout,stderr) = ossl.communicate()
		ret = ossl.returncode
		
		if ret==1:
			status=-2
			outputText = 'The key is a debian weak key. '
		else:
			if ret==0:
				status=1
				outputText = 'The key is no debian weak key. '
			else:
				raise Exception('Unknown return code of openssl-vulnkey')	
		
		return status, outputText, []

	def __init__(self, engine=None, parameter=0, shared=None):
		super(DebianWeakKey,self).__init__(engine, parameter, shared)