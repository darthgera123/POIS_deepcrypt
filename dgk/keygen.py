from sympy import nextprime, randprime
from sympy.core.numbers import mod_inverse
from sympy.ntheory import isprime
import random
import math
import gensafeprime
import numpy as np
import threading
import concurrent.futures
import os

def gen_p_q(u, v, k):
	print(u, v, k)
	while(1):
		temp1 = 2 * u * v
		sz = k//2 - temp1.bit_length()
		prand = gensafeprime.generate(sz)
		p = temp1*prand + 1
		if isprime(p):
			return p, prand

def rand_calc(p, partials_p):
	print(p, partials_p)
	while(1):
		hrandp = random.randint(0, p-1)
		if(hrandp == 1 or math.gcd(hrandp, p) != 1):
			continue
		f = False
		for prod in partials_p:
			f = f | (pow(hrandp, prod, p) == 1)		
			if(f):
				break
		if(not f):
			break
	return hrandp


def keygen(k, t, l, save_dir, save_in_file=True, gen_dlut=False):

	# generate distinct primes vp and vq
	vp = gensafeprime.generate(t)
	while(1):
		vq = gensafeprime.generate(t)
		if vp != vq:
			break

	# generate u to be the prime just greater than 2^l+2
	u = nextprime(pow(2, l+2))

	# generate prime p s.t. vp | p-1 and u | p-1
	print("Generating p....")

	print("Generating q....")
	vals = [[u, vp, k], [u, vq, k]]

	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(gen_p_q, *param) for param in vals]
	p, q = [f.result() for f in futures]
	p, prand = p
	q, qrand = q
	print("p, q Generated")

	# calc n
	n = p*q

	# finding h
	partials_p = [2*u*vp, 2*u*prand, 2*vp*prand, prand*vp*u]

	partials_q = [2*u*vq, 2*u*qrand, 2*vq*qrand, qrand*vq*u]
	vals = [[p, partials_p], [q, partials_q]]
	print("Generating hrand......")
	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(rand_calc, *param) for param in vals]

	hrandp, hrandq = [f.result() for f in futures]
	
	hrand = (hrandp*q*mod_inverse(q, p) + hrandq*p*mod_inverse(p, q)) % n
	h = pow(hrand, 2*u*prand*qrand, n)
	print("Generated hrand......")



	#finding g
	partials_p = [2*u*vp, 2*u*prand, 2*vp*prand, prand*vp*u]

	partials_q = [2*u*vq, 2*u*qrand, 2*vq*qrand, qrand*vq*u]
	vals = [[p, partials_p], [q, partials_q]]
	print("Generating grand......")
	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(rand_calc, *param) for param in vals]

	grandp, grandq = [f.result() for f in futures]

	grand = (hrandp*q*mod_inverse(q, p) + hrandq*p*mod_inverse(p, q)) % n
	g = pow(grand, 2*prand*qrand, n)
	print("Generated grand......")


	priv, pub = {}, {}
	priv['p'], priv['q'], priv['vp'], priv['vq'] = p, q, \
										 			vp, vq
	pub['n'], pub['g'], pub['h'], pub['u'], pub['t'] = n, g, \
										 				h, u, t

	if(gen_dlut):
		print("Generating dlut....")
		priv['dlut'] = []
		for i in range(pub['u']):
			if(i%10000 == 0):
				print(i)
			priv['dlut'].append(pow(pub['g'], priv['vp']*i, priv['p']))
		priv['dlut'] = np.array(priv['dlut'])

	if(save_in_file):
		np.save(os.path.join(save_dir, "priv.npy"), priv)
		np.save(os.path.join(save_dir, "pub.npy"), pub)

	return priv, pub



