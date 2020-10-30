# POIS_deepcrypt

### Requirements: Python3
- sympy
- numpy
- gensafeprime

### Paillier Cryptosystem:
- Python library - paillierlib
-  Installation - pip install paillierlib
- Usage:
-    Generating key pair - paillier.keygen()
-   encryption - paillier.encrypt(message, keypair.public_key)
-   decryption - paillier.decrypt(message, keypair.private_key)
-   Homomorphic operations - Use normal operations in the encrypted domain as well, it internally takes care of it.
-   Doc - https://pypi.org/project/paillierlib/

## Knows Issues
- Convert the adhoc style to client-server
- Final step of `comparison/dgk_comp.py`
- DGK decryption the power according to the original algo should be vp*vq, but we have used just vp.
- Equality case in comparison.
- Currently the code for veu11 is not client-server based so when comparing 2 unencrypted numbers using dgk_compare, key for goldwasser micali is generated in veu11.py and the public key is passed as an argument to dgk compare function. Need to fix this when moving to client - server based code.
- For testing purpose of veu11, currently the code returns the decrypted output. It should return only the encrypted bit. Fix this after testing

## IMPORTING FILES
- write these 2 lines in a script setup.py and save it in parent directory of POIS_deepcrypt
- line 1: from setuptools import setup, find_packages
- line 2: setup(name='myproject', version='1.0', packages=find_packages())
- run 'pip3 install -e .' in parent directory of POIS_deepcrypt	
- Use ' from POIS_deepcrypt.dir1.dir2 import file ' to import a file anywhere , then use file.function()  
