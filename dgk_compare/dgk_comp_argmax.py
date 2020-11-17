# TODO: This is adhoc code, make it work in a client-server fashion
import sys
sys.path.append("../")
import dgk
import numpy as np
import random
from sympy.core.numbers import mod_inverse
import goldwasser_micali as gm  

def get_bits(n, l):
	bits = []
	for i in range(l):
		bits.append(n & 1)
		n = n >> 1
	return bits

# change this if want to generate keys
generate_keys = False

if(generate_keys):
	#keygen without dlut and with save in file (default)
	dgk.keygen(2048, 160, 18)

pub_key = "../dgk/pub.npy"
priv_key = "../dgk/priv.npy"
pub = np.load(pub_key, allow_pickle=True).item()
priv = np.load(priv_key, allow_pickle=True).item()



def step2_B(c,pk):
	delb = 0
	for ci in c:
		ci_iszero = dgk.decrypt_iszero(ci, priv)
		if(ci_iszero):
			delb = 1
			break
	N, _ = pk
	c2 = gm.encrypt(delb, pk)
	c2_bit = list(c2)[0]
	return c2_bit

#In this version B Calls this
def compare(x, y_enc , l, pk):

	x_b = get_bits(x, l)
	x_enc = []
	for b in x_b:
		x_enc.append(dgk.encrypt(b, pub))
	x_enc = np.array(x_enc)
	one_enc = dgk.encrypt(1, pub)
	xxory = []

	for i in range(l):
		if x_b[i] == 0:
			xxory.append(y_enc[i])
		else:
			xxory.append(
					(
					(one_enc%pub['n']) *
					(mod_inverse(y_enc[i], pub['n'])%pub['n'])
					)%pub['n']
				)
	xxory = np.array(xxory)

	dela = np.random.randint(0, 2)
	s = 1 - 2*dela
	s_enc = dgk.encrypt(s, pub)

	# precompute xor cubes
	xor3precomp = [1]*l
	i = l-2
	while(i >= 0):
		xor3precomp[i] = (
						(pow(xxory[i+1], 3, pub['n'])%pub['n']) *
						(xor3precomp[i+1]%pub['n'])
						)%pub['n']
		i -= 1
	# compute [c]
	c = []
	for i in range(l):
		temp = (
				(s_enc%pub['n']) *
				(x_enc[i]%pub['n']) *
				(mod_inverse(y_enc[i], pub['n']))%pub['n'] *
				(xor3precomp[i]%pub['n'])
				)%pub['n']
		r = np.random.randint(1, pub['u'])
		r_dash = random.getrandbits(int(2.5*pub['t']))
		temp = (
				pow(temp, r, pub['n']) *
				pow(pub['h'], r_dash, pub['n'])
			)%pub['n']
		c.append(temp)
	c = np.array(c)
	# shuffle c 
	np.random.shuffle(c)
	
	N, _ = pk

	c1 = gm.encrypt(dela, pk)

	one = gm.encrypt(1, pk)	

	c1_bit = list(c1)[0]

	one_bit = list(one)[0]

	##############################################################################################################
	c2_bit = step2_B(c,pk)
	##############################################################################################################

	return (((c1_bit%N * c2_bit%N)%N) * one_bit%N)%N




