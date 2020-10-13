from sympy import nextprime, randprime
from sympy.core.numbers import mod_inverse
from sympy.ntheory import isprime
import random
import math
import gensafeprime
import numpy as np


def decrypt_iszero(c, priv):

	m_dash = pow(c, priv['vp'], priv['p'])
	if(m_dash == 1):
		return True
	else:
		return False

def decrypt(c, priv):

	m_dash = pow(c, priv['vp'], priv['p'])
	if(m_dash == 1):
		m_dash = 0
	else:
		m_dash = np.argwhere(priv['dlut'] == m_dash)[0][0]

	return m_dash