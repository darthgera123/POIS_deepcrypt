import math
import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm
from POIS_deepcrypt.veu11 import veu11 as CMP

key = paillier.keygen()

privk = key.private_key
pubk = key.public_key


a=[]
for i in range(10):
	x = random.randint(1,100)
	a.append(x)
a = np.array(a)

inp=[]
for num in a:
	inp.append(paillier.encrypt(mpz(num),pubk))
inp=np.array(inp)


def compare_enc(mxval,shuf_inp,l,pubk):
	global key
	privk = key.private_key
	print(CMP.compare(mxval,shuf_inp,l,pubk,privk))

def handler(inp,l,pubk):
	perm=np.arange(0,len(inp))
	random.shuffle(perm)
	shuf_inp = inp[ perm ]
	mxval = shuf_inp[ 0 ]
	# for i in range(len(shuf_inp)):
	compare_enc(mxval,shuf_inp[1], l , pubk)

handler(inp,10,pubk)

