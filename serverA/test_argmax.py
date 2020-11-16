import random	
import requests
from tqdm import tqdm
from paillierlib import paillier
import numpy as np
from gmpy2 import mpz
import json
import math

def argmax_handler(my_inp):
	requests.post("http://127.0.0.1:8000/veu11_init")
	pbk = requests.post("http://127.0.0.1:5000/share_public_key")

	kg = pbk.json()['pbk']
	pubk = paillier.PaillierPublicKey(n=mpz(kg["n"]), g=mpz(kg["g"]))

	def serializeANDenc_arr( my_inp ): 
		mx = max(my_inp)
		l = int(math.log2(abs(mx)))
		l += 10			
		gg = [ ]
		for i in range(len(my_inp)):
			x = paillier.encrypt( mpz(my_inp[ i ]) ,  pubk )
			gg.append( x )
		s1=str(gg[0].c)
		s2=str(gg[0].n)
		for i in range(1,len(gg)):
			s1=s1+";"+str(gg[i].c)
			s2=s2+";"+str(gg[i].n)
		dic={"a1":s1,"a2":s2,"a3":l}
		return dic


	getans = requests.post("http://127.0.0.1:5000/argmax_vector_nokey", json={"inp":serializeANDenc_arr( my_inp )} )

	print(int(getans.json()['ans']["answer"]) , actual_best)


def getInput():
	leng = 20
	my_inp = []
	for i in range(leng):
		my_inp.append(random.randint(-2**40,2**40))
	my_inp=np.array(my_inp)

	actual_best = np.argmax( my_inp )
	return my_inp,actual_best

########################################################################################################################################
my_inp,actual_best = getInput()
print(my_inp)
argmax_handler(my_inp)