from sympy import nextprime, randprime
from sympy.core.numbers import mod_inverse
from sympy.ntheory import isprime
import random
import math
import gensafeprime
import numpy as np

def keygen(k, t, l, save_in_file=True, gen_dlut=False):

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
	while(1):
		temp1 = 2*u*vp
		sz = k//2 - temp1.bit_length()
		prand = gensafeprime.generate(sz)
		p = temp1*prand + 1
		if isprime(p):
			break

	print("Generating q....")
	# generate prime q s.t. vq | q-1 and u | q-1
	while(1):
		temp1 = 2*u*vq
		sz = k//2 - temp1.bit_length()
		qrand = gensafeprime.generate(sz)
		q = temp1*qrand + 1
		if isprime(q):
			break

	# calc n
	n = p*q

	# finding h
	partials_p = [2*u*vp, 2*u*prand, 2*vp*prand, prand*vp*u]
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

	partials_q = [2*u*vq, 2*u*qrand, 2*vq*qrand, qrand*vq*u]
	while(1):
		hrandq = random.randint(0, q-1)
		if(hrandq == 1 or math.gcd(hrandq, q) != 1):
			continue
		f = False
		for prod in partials_q:
			f = f | (pow(hrandq, prod, q) == 1)		
			if(f):
				break
		if(not f):
			break

	hrand = (hrandp*q*mod_inverse(q, p) + hrandq*p*mod_inverse(p, q)) % n
	h = pow(hrand, 2*u*prand*qrand, n)


	#finding g
	partials_p = [2*u*vp, 2*u*prand, 2*vp*prand, prand*vp*u]
	while(1):
		grandp = random.randint(0, p-1)
		if(grandp == 1 or math.gcd(grandp, p) != 1):
			continue
		f = False
		for prod in partials_p:
			f = f | (pow(grandp, prod, p) == 1)		# modp or modp-1
			if(f):
				break
		if(not f):
			break

	partials_q = [2*u*vq, 2*u*qrand, 2*vq*qrand, qrand*vq*u]
	while(1):
		grandq = random.randint(0, q-1)
		if(grandq == 1 or math.gcd(grandq, q) != 1):
			continue
		f = False
		for prod in partials_q:
			f = f | (pow(grandq, prod, q) == 1)		# modp or modp-1
			if(f):
				break
		if(not f):
			break

	grand = (hrandp*q*mod_inverse(q, p) + hrandq*p*mod_inverse(p, q)) % n
	g = pow(grand, 2*prand*qrand, n)


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
		np.save("priv.npy", priv)
		np.save("pub.npy", pub)

	return priv, pub



