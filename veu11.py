import random
import dgk_compare
import goldwasser_micali as gm 
from paillierlib import paillier
from gmpy2 import mpz

def MSB(x, l):
	return bin(x)[2:].zfill(l+1)[0]

def compare(encrypted_a, encrypted_b, l, pk, privk):
	# -------------------A-----------------------------
	x = encrypted_b + paillier.encrypt(pow(2, l), pk) - encrypted_a
	r = random.randint(0, 1e18)
	z = x + paillier.encrypt(mpz(r), pk)
	c = r % pow(2, l)

	#---------------------B----------------------------
	z_dec = paillier.decrypt(mpz(z), privk)
	d = z_dec % pow(2, l)

	#-----------------A and B compute encrypted t -----
	kp = gm.generate_key()
	qr_pk = kp["pub"]
	qr_privk = kp["priv"]
	t = dgk_compare.compare(c, d, l, qr_pk, qr_privk)

	# -------------------A-----------------------------
	if MSB(r, l)=='0':
		r_l = gm.encrypt(0, qr_pk)
	else:
		r_l = gm.encrypt(1, qr_pk)

	# -------------------B-----------------------------
	if MSB(z_dec, l)=='0':
		z_l = gm.encrypt(0, qr_pk)
	else:
		z_l = gm.encrypt(1, qr_pk)

	# -------------------A-----------------------------
	N, _ = qr_pk
	t_ = (z_l[0] * r_l[0])%N
	t = (t_ * t)%N

	print(gm.decrypt([t], qr_privk))
	return t

key_pair = paillier.keygen()
encrypted_a = paillier.encrypt(mpz(15), key_pair.public_key)
encrypted_b = paillier.encrypt(mpz(14), key_pair.public_key)

print(compare(encrypted_a, encrypted_b, 4, key_pair.public_key, key_pair.private_key))
