from keygen import *
from encrypt import *
from decrypt import  *
import numpy as np

# change this if want to generate keys
generate_keys = True

if(generate_keys):
	#keygen without dlut and with save in file (default)
	keygen(2048, 160, 18, None)

pub = np.load("pub.npy", allow_pickle=True).item()
priv = np.load("priv.npy", allow_pickle=True).item()

#100 iszero tests
for i in range(100):
	m = np.random.randint(0, 1)
	c = encrypt(m, pub)
	m_iszero = decrypt_iszero(c, priv)

	if (m == 0 and not m_iszero) or (m != 0 and m_iszero):
		print("Failed!!!!")
		quit()

print("Success!!!!")