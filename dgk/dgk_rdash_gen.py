import random 
import numpy as np

r_dash = []
pub = np.load("./pub.npy", allow_pickle=True).item()
for i in range(1000):
	print(i)
	r = random.getrandbits(int(2.5*pub['t']))
	r_dash.append(pow(pub['h'], r, pub['n']))
np.save("./r_dash.npy", r_dash)