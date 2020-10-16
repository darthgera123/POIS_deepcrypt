# TODO: This is adhoc code, make it work in a client-server fashion
import sys
sys.path.append("../")
import dgk
import numpy as np
import random
from sympy.core.numbers import mod_inverse

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


l = 4

#-----------------B-------------------
y = random.getrandbits(l)
print("y: ", y)
# get bits
y_b = get_bits(y, l)
# get encrypted bits
y_enc = []
for b in y_b:
	y_enc.append(dgk.encrypt(b, pub))
y_enc = np.array(y_enc)


#-----------------A-------------------
x = random.getrandbits(l)
print("x: ", x)
# get bits
x_b = get_bits(x, l)
# get encrypted bits
x_enc = []
for b in x_b:
	x_enc.append(dgk.encrypt(b, pub))
x_enc = np.array(x_enc)
# get encryption of 1
one_enc = dgk.encrypt(1, pub)
# get [x xor y]
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

# make s
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


#-----------------B-------------------
delb = 0
for ci in c:
	ci_iszero = dgk.decrypt_iszero(ci, priv)
	if(ci_iszero):
		delb = 1
		break


#-----------------AB-------------------
# how to use the values dela delb in an actual algo??
print("IS x <= y ? ", bool(dela^delb))

