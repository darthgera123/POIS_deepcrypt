import math
import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm
from POIS_deepcrypt.veu11 import veu11_argmax as CMP
from POIS_deepcrypt.goldwasser_micali import goldwasser_micali as gm 

key = paillier.keygen()

privk = key.private_key
pubk = key.public_key


def getRandomInp():
	a=[]
	for i in range(5):
		x = random.randint(1,31)
		a.append(x)
	a = np.array(a)

	print(a)
	inp=[]
	for num in a:
		inp.append(paillier.encrypt(mpz(num),pubk))
	inp=np.array(inp)

	return inp

private_b_var = 0

def refresh_b( num ):
	global pubk , privk
	plainval = paillier.decrypt( num , privk )
	re_enc = paillier.encrypt( plainval , pubk )
	return re_enc

def b_handler( mx_rand , ai_rand , l , enc_bit , idx , pubk):
	
	qr_privk = CMP.get_GM_privk_B()

	isless = bool(gm.decrypt([enc_bit],qr_privk))

	if isless:
		global private_b_var
		private_b_var = idx
		vi = refresh_b( ai_rand )
		bit_paillier = paillier.encrypt(1,pubk)
	else:	
		vi = refresh_b( mx_rand )
		bit_paillier = paillier.encrypt(0,pubk)

	return bit_paillier , vi	

def askB_for_index():
	global private_b_var
	return private_b_var

# party A function
def handler_A(inp,l,pubk,privk):
	
	perm=np.arange(0,len(inp))
	random.shuffle(perm)
	shuf_inp = inp[ perm ]
	mxval = shuf_inp[ 0 ]

	# for i in shuf_inp:
	# 	print(paillier.decrypt(i,privk),end=' ')
	# print()	

	# for i in tqdm(range(len(shuf_inp))):
	for i in range(len(shuf_inp)):
		
		ai = shuf_inp[ i ]	
		
		enc_bit = CMP.compare_A(mxval , ai , l , pubk , privk )
		
		r = random.getrandbits( 2 * l + 1 )
		s = random.getrandbits( 2 * l + 1 )
		
		enc_r = paillier.encrypt( r , pubk )
		enc_s = paillier.encrypt( s , pubk )

		mx_rand = mxval + enc_r
		ai_rand = ai + enc_s

		bi , vi = b_handler( mx_rand , ai_rand , l , enc_bit , i , pubk)

		one_enc = paillier.encrypt(mpz(1),pubk)

		remove_r = ( bi - one_enc ) * r
		remove_s = bi * s

		vi = vi + remove_r
		vi = vi - remove_s

		mxval = vi

		# print( paillier.decrypt( mxval , privk ) , "###############################################" )

	shuf_idx = askB_for_index()

	return perm[ shuf_idx ]

inp = getRandomInp()
print( handler_A( inp , 6 , pubk , privk ) )

