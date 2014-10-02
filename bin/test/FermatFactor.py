from Test import Test
import gmpy as gmp
from gmpy import mpz

class FermatFactor(Test):		
	def run(self, key, testRun, keyReference, client, makePerm=True):
		res = extFactor(key.n, self.parameter)
		if res:
			status = -2
			outputText = 'A prime factor was found. '
		else:
			status = 1
			outputText = 'No nearly equal factors with maximal difference ' + str(2*self.parameter) + ' found. '
		return status, outputText, []

	def __init__(self, engine=None, parameter=0, shared=None):
		super(FermatFactor,self).__init__(engine, parameter, shared)		

#Basic Fermat Factoring algorithm
def Factor(n, parameter):
	if n % 2 == 0:
		return true

	a = gmp.sqrt(n)
	b2 = a**2-n
	bound = a + parameter

	while not gmp.is_square(b2) and a<=bound:
		b2=b2+2*a+1
		a+=1
	
	if a > bound:
		return False
	else:
		return True
#Better Fermat Factoring algorithm
#Speedup factor 20 
def extFactor(n, parameter):
	def fermat(n, astart, aend, astep, k):		
		if k==len(moduli) or (aend-astart)/astep < 2:
			lista = [astart+i*astep for i in range(0,((aend-astart)/astep)+1)]
			listb2 = [a**2 - n for a in lista]
			return any([gmp.is_square(b2) for b2 in listb2])
		
		result = []
		mod, quadRes = moduli[k]
		a = astart
		
		for i in range(0, min(mod, (aend-astart)/astep + 1)):
			if ((a**2-n) % mod) in quadRes:
				result.append(fermat(n, a, aend, astep*mod, k+1))
			a+=astep
		return any(result)
		
	a=gmp.sqrt(n)
	return fermat(n,a, a+parameter, 1, 0)
	
	
moduli = []
moduli.append((mpz(16), set([mpz(k) for k in [0,1,4,9]])))
p = 2
for i in range(1,20):
	p = gmp.next_prime(p)
	mod = p
	quadRes = set()
	for k in range(1,mod+1):
		quadRes.add(k**2 % mod)
	
	moduli.append((mod, quadRes))
	