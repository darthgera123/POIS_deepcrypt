import numpy as np
import random
import requests
from paillierlib import paillier
from gmpy2 import mpz, mpfr


def paillier_enc(x, pub_key):
    return paillier.encrypt(mpz(x), pub_key)


def encrypt_weights(weights, public_key):
    encrypted_weights = []
    for w in weights:
        encrypted_class = [paillier_enc(xi, public_key) for xi in w.tolist()]
        encrypted_weights.append(encrypted_class)
    return encrypted_weights

requests.post("http://127.0.0.1:8000/veu11/init")
inp_vec = np.random.randint(low=0, high=10000, size=10).tolist()
weights = np.random.randint(low=0, high=10000, size=(5, 10))

key_pair = np.load("./PAILLIER_KEY.npy", allow_pickle=True)[0]
encrypted_weights = encrypt_weights(weights, key_pair.public_key)
np.save("./encrypted_weights.npy", np.asarray(encrypted_weights))
response = requests.post("http://127.0.0.1:5001/hyperplane_handler", json={
    "vector": inp_vec
})
inp1_vec = np.asarray(inp_vec).reshape(1, 10)
index1 = np.argmax(np.dot(inp1_vec, weights.T))
# print(index1, response.json())
if index1 == int(response.json()['ans']['answer']):
    print("Success")
