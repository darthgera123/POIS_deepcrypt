from paillierlib import paillier
import numpy as np
from gmpy2 import mpz
import POIS_deepcrypt.goldwasser_micali as gm 

k=paillier.keygen()
a=np.array([k])
np.save("./PAILLIER_KEY",a)

g=gm.generate_key(1024)
b=np.array([g])
np.save("./GM_KEY",b)
