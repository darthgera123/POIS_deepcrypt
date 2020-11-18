import random	
import requests
from tqdm import tqdm
from paillierlib import paillier
import numpy as np
from gmpy2 import mpz
import json
import math
import time

def serializeANDenc_arr( my_inp , pubk  ): 
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

def serializeArr( gg , l ): 
	s1=str(gg[0].c)
	s2=str(gg[0].n)
	for i in range(1,len(gg)):
		s1=s1+";"+str(gg[i].c)
		s2=s2+";"+str(gg[i].n)
	dic={"a1":s1,"a2":s2,"a3":l}
	return dic

def argmax_handler(my_inp):
	global T

	requests.post("http://127.0.0.1:8000/veu11/init")
	pbk = requests.post("http://127.0.0.1:5000/share_public_key")

	kg = pbk.json()['pbk']
	pubk = paillier.PaillierPublicKey(n=mpz(kg["n"]), g=mpz(kg["g"]))

	print("Keygen done: ", time.time() - T)
	T = time.time()

	getans = requests.post("http://127.0.0.1:5000/argmax/vector_nokey", json={"inp":serializeANDenc_arr( my_inp,pubk )})

	print("ans got: ", time.time() - T)
	T = time.time()	

	print(int(getans.json()['ans']["answer"]) , actual_best)

def argmax_handler_enc( gg , l ):
	requests.post("http://127.0.0.1:8000/veu11/init")
	# pbk = requests.post("http://127.0.0.1:5000/share_public_key")

	# kg = pbk.json()['pbk']
	# pubk = paillier.PaillierPublicKey(n=mpz(kg["n"]), g=mpz(kg["g"]))

	getans = requests.post("http://127.0.0.1:5000/argmax/vector_nokey", json={"inp":serializeArr( gg , l )})


	return int(getans.json()['ans']["answer"])
	# print(int(getans.json()['ans']["answer"]))


def getInput():
	leng = 10
	s = 2**70
	my_inp = []
	for i in range(leng):
		my_inp.append(random.randint(1,s))
	my_inp=np.array(my_inp)

	actual_best = np.argmax( my_inp )
	return my_inp,actual_best

#######################################################################################################################################
T = time.time()
my_inp,actual_best = getInput()
print(my_inp)
print("Input generated: ", time.time() - T)
T = time.time()
argmax_handler(my_inp)

