import random	
import requests
from tqdm import tqdm
from paillierlib import paillier
import numpy as np
from gmpy2 import mpz
import json
import math


def serializeArr( gg , l ): 
	s1=str(gg[0].c)
	s2=str(gg[0].n)
	for i in range(1,len(gg)):
		s1=s1+";"+str(gg[i].c)
		s2=s2+";"+str(gg[i].n)
	dic={"a1":s1,"a2":s2,"a3":l}
	return dic




	return int(getans.json()['ans']["answer"])

def bayes():

	requests.post("http://127.0.0.1:8000/veu11_init")

	l = 85
	conditional_prob_list = np.load("./COP_ENC.npy")
	
	class_prior_list = np.load("./CLP_ENC.npy")
	sx,sy,sz=conditional_prob_list.shape
	dict_send = { "clp":serializeArr(class_prior_list.flatten() , l),"cop":serializeArr(conditional_prob_list.flatten() , l),"sx":str(sx),"sy":str(sy),"sz":str(sz)}
	
	ret = requests.post("http://127.0.0.1:5001/bayes_handler", json=dict_send)

	corr = int(ret.json()['correct'])
	total = int(ret.json()['tot'])
	accuracy = (corr/total)*100
	print("ENCRYPTED ACCURACY IS ",accuracy)	


bayes()