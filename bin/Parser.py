from subprocess import Popen,PIPE
from key.RSA import RSA
import logging


def getParser(string):
	if hasParser(string):
		keyFormat, keyType = getParam(string)
		methodname = keyFormat + '_' + keyType
		return globals()[methodname]
	else:
		return
			
def getParam(string):
	if string.startswith('-----BEGIN CERTIFICATE-----'):
		return 'X509', _opensslAlgo(string, 'x509')
	if string.startswith('-----BEGIN CERTIFICATE REQUEST-----') or string.startswith('-----BEGIN NEW CERTIFICATE REQUEST-----'):
		return 'PCKS10', _opensslAlgo(string, 'req')
	if string.startswith('-----BEGIN RSA PRIVATE KEY-----'):
		return 'PrivK', 'RSA'
	if string.startswith('-----BEGIN PUBLIC KEY-----'):
		return 'PubK', 'RSA'
	return
	
def hasParser(string):
	keyFormat, keyType = getParam(string)
	methodname = keyFormat + '_' + keyType
	return methodname in globals()
		
def parse(string):
	if hasParser(string):
		return getParser(string)(string)
	else:
		return
		
	
		
def _opensslPubK(string, param, programm):
	
	ossl = Popen(['openssl'] + param , stdout=PIPE, stderr=PIPE, stdin=PIPE)
	(stdout,stderr) = ossl.communicate(string)

	res = stdout
	list = stdout.split('\n')

	if list[0] != ("-----BEGIN PUBLIC KEY-----") or list[-2] != ("-----END PUBLIC KEY-----"):
		logging.warning('Could not extract public key from: \n' + string)
		return
		
	return PubK_RSA(res)
	
def _opensslAlgo(string, cmd):
	ossl = Popen(['openssl', cmd , '-text', '-noout'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
	(stdout,stderr) = ossl.communicate(string)

	if 'Public Key Algorithm: dsaEncryption' in stdout:
		return 'DSA'
	if 'Public Key Algorithm: rsaEncryption' in stdout:	
		return 'RSA'
	
	logging.warning('Unknown key format inserted: \n' + string)
	return
	
	
def PCKS10_RSA(string):
	return _opensslPubK(string, ['req','-pubkey', '-noout'], 'PCKS10')

	
def X509_RSA(string):
	return _opensslPubK(string, ['x509','-pubkey', '-noout'], 'X509')
		
def PrivK_RSA(string):
	return _opensslPubK(string, ['rsa', '-pubout'], 'PrivK')
		
def PubK_RSA(string):
	ossl = Popen(['openssl','rsa','-pubin','-text','-noout'] , stdout=PIPE, stderr=PIPE, stdin=PIPE)
	(stdout,stderr) = ossl.communicate(string)
	list = stdout.split('\n')

	key = RSA()
	try:
		key.e=long(list[-2].split(' ')[1])	
		key.n=long(''.join(''.join(''.join(list[2:-2]).split()).split(':')),16)
		return key
	except:
		logging.warning('Could not extract key from: \n' + string)
		return
	