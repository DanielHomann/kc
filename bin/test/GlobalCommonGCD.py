from GlobalTest import GlobalTest
import gmpy as gmp
from gmpy import mpz

class GlobalCommonGCD(GlobalTest):

	def run(self, keys, testRun, keyReferences, client, makePerm=True):
		
		tree=[[]]
		moduli = []
		for key, keyReference in zip(keys, keyReferences):
			z = mpz(key.modulus)
			tree[0].append(z)
			moduli.append((z, keyReference))
			

		while len(tree[-1])>1:
			row=[]
			for k in range(0,len(tree[-1]),2):
				if k+1<len(tree[-1]):	
					row.append(tree[-1][k]*tree[-1][k+1])
				else:
					row.append(tree[-1][k])
			tree.append(row)
	
		for k in range(len(tree)-2,-1,-1):
			for i in range(0,len(tree[k])):
				tree[k][i]= tree[k+1][i//2] % tree[k][i]**2 

		res=[]
		for k in range(0,len(tree[0])):
			res.append( gmp.gcd(moduli[k][0]**2, tree[0][k]) // moduli[k][0])	
		
		revokes = []
		for k in range(0,len(res)):
			if res[k]>1:
				#print 'CommonGCD  found'
				#print moduli[k][1]
				#print res[k] == moduli[k][0]
				#print res[k]
				#print '---------------------------------'
				
				revokes.append(keyReferences[k])
		
		if len(revokes) == 0:
			status = 1
			outputText = 'No common GCD found'
		else:
			status = -2
			outputText = 'Common GCDs found'
			
		return status, outputText, revokes