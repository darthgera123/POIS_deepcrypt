import sys
sys.path.append("../")
import dgk
import numpy as np
import random
from sympy.core.numbers import mod_inverse
# change this if want to generate keys
from paillierlib import paillier
from gmpy2 import mpz
# generate_keys = False
random.seed = 42
N = 2048
key_pair = paillier.keygen()
pub = key_pair.public_key
priv = key_pair.private_key


def dot(a,b):

    vector_b_encrypt = []
    for each in b:
        each = mpz(each)
        c1 = paillier.encrypt(each, pub)
        vector_b_encrypt.append(c1)


    fval = 0
    for ind,each in enumerate(vector_b_encrypt):
        c2 = mpz(a[ind])
        c1 = each
        x = paillier.decrypt(c1 * c2, priv)
        fval += x
    return fval