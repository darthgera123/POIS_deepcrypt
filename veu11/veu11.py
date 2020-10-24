import random
from tqdm import tqdm
import dgk_compare
import goldwasser_micali as gm 
from paillierlib import paillier
from gmpy2 import mpz

def MSB(x, l):
	return bool(x & pow(2, l))

def compare(encrypted_a, encrypted_b, l, pk, privk):
	# -------------------A-----------------------------
	x = encrypted_b + paillier.encrypt(pow(2, l), pk) - encrypted_a
	r = random.getrandbits(l + 2)
	z = x + paillier.encrypt(mpz(r), pk)
	c = r % pow(2, l)

	#---------------------B----------------------------
	z_dec = paillier.decrypt(z, privk)
	d = z_dec % pow(2, l)

	#-----------------A and B compute encrypted t -----
	kp = gm.generate_key(1024)
	qr_pk = kp["pub"]
	qr_privk = kp["priv"]
	t = dgk_compare.compare(c, d, l, qr_pk)

	# -------------------A-----------------------------
	if MSB(r, l):
		r_l = gm.encrypt(1, qr_pk)
	else:
		r_l = gm.encrypt(0, qr_pk)

	# -------------------B-----------------------------
	if MSB(z_dec, l):
		z_l = gm.encrypt(1, qr_pk)
	else:
		z_l = gm.encrypt(0, qr_pk)

	# -------------------A-----------------------------
	N, _ = qr_pk
	t_ = (z_l[0]%N * r_l[0]%N)%N
	t = (t_%N * t%N)%N

	return t, bool(gm.decrypt([t], qr_privk))
