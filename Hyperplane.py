import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm

def getFeatureValues():
	#Random generation
	feature_values = []
	mapping = []
	num_features = 2
	dist_values_feature = 2

	for i in range(num_features):
		mapping.append({})
		values = []
		for j in range(dist_values_feature):
			rand_val = random.randint(0,1000)
			values.append( rand_val )

		feature_values.append(values)

	ind = 0	
	for f_list in feature_values:
		idx = 0	
		for val in f_list:
			mapping[ ind ][ val ] = idx
			idx += 1
		ind += 1	

	return 	feature_values , mapping	


def genInput(mapping):
	#random input generated
	inp=[]
	for values in mapping:
		possible = []
		for key in values:
			possible.append(key)
		inp.append(random.choice(possible))	
	return inp	


feature_values,mapping = getFeatureValues()
inp_vec = genInput(mapping)

print(inp_vec)

key_pair = paillier.keygen()

def paillier_enc(x):
	global key_pair

	return paillier.encrypt( mpz(x) , key_pair.public_key)

print(paillier_enc(inp_vec[0]))	