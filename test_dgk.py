import dgk
import numpy as np
import random
import time
# change this if want to generate keys
generate_keys = True
start = time.time()
if(generate_keys):
	#keygen without dlut and with save in file (default)
	dgk.keygen(2048, 160, 18, ".")
end = time.time()

print(end - start)
pub = np.load("dgk/pub.npy", allow_pickle=True).item()
priv = np.load("dgk/priv.npy", allow_pickle=True).item()

#100 iszero tests
for i in range(100):
	m = np.random.randint(0, 2)
	c = dgk.encrypt(m, pub)
	m_iszero = dgk.decrypt_iszero(c, priv)

	if (m == 0 and not m_iszero) or (m != 0 and m_iszero):
		print("Failed!!!!")
		quit()

print("Success!!!!")


# Checking dot product
a = random.sample(range(1,100),5)
b = random.sample(range(1,100),5)

print(np.dot(a,b))
x = dgk.dot(a,b)
print(x)