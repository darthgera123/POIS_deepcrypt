import random
from tqdm import tqdm
from POIS_deepcrypt.dgk import *
from POIS_deepcrypt.dgk_compare import dgk_comp_argmax as DGK
from POIS_deepcrypt.goldwasser_micali import goldwasser_micali as gm 
from paillierlib import paillier
from gmpy2 import mpz


pub_key = "../dgk/pub.npy"
priv_key = "../dgk/priv.npy"
pub = np.load(pub_key, allow_pickle=True).item()
priv = np.load(priv_key, allow_pickle=True).item()

def MSB(x, l):
	return bool(x & pow(2, l))

def get_bits(n, l):
	bits = []
	for i in range(l):
		bits.append(n & 1)
		n = n >> 1
	return bits

def enc_B(y,l):

	y_b = get_bits(y, l)
	y_enc = []
	for b in y_b:
		y_enc.append(dgk.encrypt(b, pub))
	y_enc = np.array(y_enc)
	return y_enc

kp = gm.generate_key(1024)
qr_pk = kp["pub"]
qr_privk = kp["priv"]

def step1_B(z , privk , l  , r_l , c):
	
	global qr_pk , qr_privk
	
	z_dec = paillier.decrypt(z, privk)
	d = z_dec % pow(2, l)
	
	if MSB(z_dec, l):
		z_l = gm.encrypt(1, qr_pk)
	else:
		z_l = gm.encrypt(0, qr_pk)
  	
	t = DGK.compare(c, enc_B(d,l) , l, qr_pk)

	N, _ = qr_pk
	t_ = (z_l[0]%N * r_l[0]%N)%N
	t = (t_%N * t%N)%N

	return t

def get_GM_privk_B():
	global qr_privk
	return qr_privk

#driven by A ie belongs to A , but changed for argmax protocol

def compare_A(encrypted_a, encrypted_b, l, pk, privk):

	# KEY REQUEST TO BE CORRECTED ALL ACROSS
	global qr_pk

	x = encrypted_b + paillier.encrypt(pow(2, l), pk) - encrypted_a
	r = random.getrandbits(l + 2)
	z = x + paillier.encrypt(mpz(r), pk)
	c = r % pow(2, l)

	if MSB(r, l):
		r_l = gm.encrypt(1, qr_pk)
	else:
		r_l = gm.encrypt(0, qr_pk)

	ask_B_tocompute = step1_B(z , privk , l  , r_l , c)	

	return ask_B_tocompute
