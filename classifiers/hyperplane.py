import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm
import POIS_deepcrypt.goldwasser_micali as gm
from POIS_deepcrypt.Naiive_Bayes.ArgMax import handler_A


def paillier_enc(x,pub_key):
	return paillier.encrypt( mpz(x) , pub_key)

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
def dot(a,b,public_key):
	"""
	Dot product. Input is 2 unencrypted values and keys. 
	Encrypt server side and then compute
	Return encrypted output
	"""
	vector_b_encrypt = []
	for each in b:
	    each = mpz(each)
	    c1 = paillier.encrypt(each, public_key)
	    vector_b_encrypt.append(c1)
	fval = []
	for ind,each in enumerate(vector_b_encrypt):
	    c2 = mpz(a[ind])
	    c1 = each
	    x = c1*c2
	    fval.append(x)
	fsum = fval[0]
	for val in fval[1:]:
		fsum+=val
	return fsum 

def compute_dot(inp_vec,weights,public_key):
	encrypted_dot_product = []
	for i in range(len(weights)):
		output = dot(inp_vec,weights[i].tolist(),public_key)
		encrypted_dot_product.append(output)
	return np.asarray(encrypted_dot_product)

encrypted_vec = compute_dot(inp_vec,weights,key_pair.public_key)

# argmax
index = handler_A(encrypted_vec,20,key_pair.public_key,key_pair.private_key)
# return class
print(index)