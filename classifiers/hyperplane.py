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
# # Creates the Goldwassier private key
# gm_key= gm.generate_key()
# gm_enc = gm.encrypt(1,gm_key['pub'])
# gm_dec = gm.decrypt(gm_enc,gm_key['priv'])
"""
Server Side functions
"""
def dot(a,b,public_key):
	"""
	Dot product. Input is 2 unencrypted values and keys. 
	Encrypt server side and then compute
	Return encrypted output
	"""
	fval = []
	for ind,each in enumerate(b):
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
		output = dot(inp_vec,weights[i],public_key)
		encrypted_dot_product.append(output)
	return np.asarray(encrypted_dot_product)

def encrypt_weights(weights,public_key):
	encrypted_weights = []
	for w in weights:
		encrypted_class = [paillier_enc(xi,public_key) for xi in w.tolist()]
		encrypted_weights.append(encrypted_class)
	return encrypted_weights

if __name__ == '__main__':
	# Input will be of the form 1*d
	# inp_vec = [1330,1550]
	inp_vec = [ 491,   20, 7384,  850,  706, 473, 238, 977, 177, 341]
	# Weights will be of the form d*k. Size of each array is d and number of arrays are k
	# weights = np.array([[-13,15],[10,-20],[-11,14]])
	# weights = np.random.randint(low=0,high=10000,size=(5,10))
	# Creates the paillier public key
	# key_pair = paillier.keygen()
	# key_pair = np.load("../serverA/PAILLIER_KEY.npy", allow_pickle=True)[0]
	# Encrypting the weights
	# encrypted_weights = encrypt_weights(weights,key_pair.public_key)
	# Computing dot product to get 1*k vector
	# print(encrypted_weights)
	# np.save("weights.npy", np.asarray(encrypted_weights))
	weights = np.load("../serverA/encrypted_weights.npy", allow_pickle=True)
	encrypted_vec = compute_dot(inp_vec,encrypted_weights,key_pair.public_key)

	# argmax
	index = handler_A(encrypted_vec,20,key_pair.public_key,key_pair.private_key)
	# return class
	print(index)

