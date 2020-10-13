from sympy import nextprime, randprime
from sympy.core.numbers import mod_inverse
from sympy.ntheory import isprime
import random
import math
import gensafeprime
import numpy as np


def encrypt(m, pub):
	r = random.getrandbits(int(2.5*pub['t']))
	c = (pow(pub['g'], m, pub['n']) * pow(pub['h'], r, pub['n'])) % pub['n']

	return c
