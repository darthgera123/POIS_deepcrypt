import math
import numpy as np
from paillierlib import paillier
from gmpy2 import mpz,mpfr
import random
import copy
from tqdm import tqdm
from POIS_deepcrypt.veu11 import veu11_argmax as CMP
from POIS_deepcrypt.goldwasser_micali import goldwasser_micali as gm 



private_b_var = 0
def getRandomInp():
	key = paillier.keygen()

	privk = key.private_key
	pubk = key.public_key
	a=[random.randint(-20000,20000),random.randint(-200000,20000),random.randint(-20000,20000)]
	# a = [1915,1383]
	# for i in range(15):
	# 	x = random.randint(-31,-1)
	# 	a.append(x)
	# a = np.array(a)

	ans = np.argmax(np.array(a))
	# print(a)
	inp=[]
	for num in a:
		inp.append(paillier.encrypt(mpz(num),pubk))
	inp=np.array(inp)

	return inp,pubk,privk,ans,a


def refresh_b( num , pubk , privk):
	# global pubk , privk
	plainval = paillier.decrypt( num , privk )
	re_enc = paillier.encrypt( plainval , pubk )
	return re_enc

def b_handler( mx_rand , ai_rand , l , enc_bit , idx , pubk , privk):
	
	qr_privk = CMP.get_GM_privk_B()

	isless = bool(gm.decrypt([enc_bit],qr_privk))

	if isless:
		global private_b_var
		private_b_var = idx
		# print("wegweg",idx,private_b_var)
		vi = refresh_b( ai_rand , pubk , privk )
		bit_paillier = paillier.encrypt(1,pubk)
	else:	
		vi = refresh_b( mx_rand , pubk , privk )
		bit_paillier = paillier.encrypt(0,pubk)

	return bit_paillier , vi	

def askB_for_index():
	global private_b_var
	return private_b_var

def handler_A(inp,l,pubk,privk):
	
	perm=np.arange(0,len(inp))
	random.shuffle(perm)
	shuf_inp = inp[ perm ]
	mxval = shuf_inp[ 0 ]
	global private_b_var
	private_b_var = 0

	for i in range(1,len(shuf_inp)):
		
		ai = shuf_inp[ i ]	
		
		enc_bit = CMP.compare_A(mxval , ai , l , pubk , privk )
		
		jj = CMP.get_GM_privk_B()
		# print(jj)
		
		r = random.getrandbits( l + 1 )
		s = random.getrandbits( l + 1 )
		
		enc_r = paillier.encrypt( r , pubk )
		enc_s = paillier.encrypt( s , pubk )

		mx_rand = mxval + enc_r
		ai_rand = ai + enc_s

		bi , vi = b_handler( mx_rand , ai_rand , l , enc_bit , i , pubk , privk)

		one_enc = paillier.encrypt(mpz(1),pubk)

		remove_r = ( bi - one_enc ) * r
		remove_s = bi * s

		vi = vi + remove_r
		vi = vi - remove_s

		# print(paillier.decrypt(mxval,privk),paillier.decrypt(ai,privk),gm.decrypt([enc_bit],jj),private_b_var,end=' ')
		mxval = vi

		# print(paillier.decrypt(mxval,privk))


	shuf_idx = askB_for_index()
	return perm[ shuf_idx ]

# for i in range(100):
# 	inp,pubk,privk,ans,ac = getRandomInp()
# 	print("#############################################")
# 	x = handler_A( inp , 40 , pubk , privk ) 
# 	if x!=ans:
# 		print(ac,x,ans)
# 		break
# 	print("#############################################")

# inp,pubk,privk,ans,ac = getRandomInp()
# x = handler_A( inp , 20 , pubk , privk ) 
# print(x)