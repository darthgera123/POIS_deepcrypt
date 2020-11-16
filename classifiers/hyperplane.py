import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm
import POIS_deepcrypt.goldwasser_micali as gm
from POIS_deepcrypt.Naiive_Bayes.ArgMax import handler_A

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
def paillier_enc(x,pub_key):
	return paillier.encrypt( mpz(x) , pub_key)


feature_values,mapping = getFeatureValues()
# Input will be of the form 1*d
inp_vec = [1330,1550]
# Weights will be of the form d*k. Size of each array is d and number of arrays are k
weights = np.array([[13,15],[10,20],[11,14]])
# Creates the paillier public key
key_pair = paillier.keygen()

# Creates the Goldwassier private key
gm_key= gm.generate_key()
gm_enc = gm.encrypt(1,gm_key['pub'])
gm_dec = gm.decrypt(gm_enc,gm_key['priv'])

# Encrypting the input with the public key
# encrypted_vec = []
# for xi in inp_vec:
# 	if xi == 0 or xi == 1:
# 		encrypted_vec.append(gm.encrypt(xi,gm_key['pub']))
# 	else:
# 		encrypted_vec.append(paillier_enc(xi,key_pair.public_key))

"""
Encrypting the weights
"""
# encrypted_weights = []
# for xi in weights:
# 	if xi == 0 or xi == 1:
# 		encrypted_weights.append(gm.encrypt(xi,gm_key['pub']))
# 	else:
# 		encrypted_weights.append(paillier_enc(xi,key_pair.public_key))

"""
Server Side functions
"""
def dot(a,b,key_pair):
	"""
	Dot product. Input is 2 unencrypted values and keys. 
	Encrypt server side and then compute
	Return encrypted output
	"""
	vector_b_encrypt = []
	for each in b:
	    each = mpz(each)
	    c1 = paillier.encrypt(each, key_pair.public_key)
	    vector_b_encrypt.append(c1)

	fval = []
	for ind,each in enumerate(vector_b_encrypt):
	    c2 = mpz(a[ind])
	    c1 = each
	    # x = paillier.decrypt(c1 * c2, key_pair.private_key)
	    x = c1*c2
	    fval.append(x)
	fsum = fval[0]
	for val in fval[1:]:
		fsum+=val
	# return paillier.encrypt(fval,key_pair.public_key)
	return fsum 

def compute_dot(inp_vec,weights,key_pair):
	encrypted_dot_product = []
	for i in range(len(weights)):
		output = dot(inp_vec,weights[i].tolist(),key_pair)
		encrypted_dot_product.append(output)
	return np.asarray(encrypted_dot_product)

encrypted_vec = compute_dot(inp_vec,weights,key_pair)
print(encrypted_vec)
# argmax
index = handler_A(encrypted_vec,10,key_pair.public_key,key_pair.private_key)
# return class
print(index)