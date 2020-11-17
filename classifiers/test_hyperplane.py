import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm
from POIS_deepcrypt.Naiive_Bayes.ArgMax import handler_A
from hyperplane import dot, compute_dot,encrypt_weights

inp_vec = np.random.randint(low=0,high=10000, size=10).tolist()
weights = np.random.randint(low=0,high=10000,size=(5,10))

key_pair = paillier.keygen()
encrypted_weights = encrypt_weights(weights,key_pair.public_key)
encrypted_vec = compute_dot(inp_vec,encrypted_weights,key_pair.public_key)
index = handler_A(encrypted_vec,30,key_pair.public_key,key_pair.private_key)

inp1_vec = np.asarray(inp_vec).reshape(1,10)
index1 = np.argmax(np.dot(inp1_vec,weights.T))
if index1 == index:
	print("Success")
else:
	print(index,index1)