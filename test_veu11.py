import random
from gmpy2 import mpz
from tqdm import tqdm
from veu11 import compare
from paillierlib import paillier

key_pair = paillier.keygen(1024)
l = 20

for i in tqdm(range(5)):
	a = random.randint(0, pow(2, l) - 1)
	b = random.randint(0, pow(2, l) - 1)
	encrypted_a = paillier.encrypt(mpz(a), key_pair.public_key)
	encrypted_b = paillier.encrypt(mpz(b), key_pair.public_key)
	for j in range(20):
		_, out = compare(encrypted_a, encrypted_b, l, key_pair.public_key, key_pair.private_key)
		if a < b and out == 0:
			print("Test Failed")
		elif a > b and out == 1:
			print("Test Failed")

