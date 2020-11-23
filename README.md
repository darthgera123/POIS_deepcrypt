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

## FASTER PAILLIER
-  replace python package ".local/lib/python3.5/site-packages/paillierlib/paillier.py" file's code with fastmod.py

## HOW TO USE
### Hyperplane Classifier
Hyperplane classifier consists of the weights encrypted at the model server and the input with the keys at the client server. At the end we get the class to which the vector belongs.    
Send a POST request to `http://127.0.0.1:5000/hyperplane_handler` with the input vector.  
+ Internally it will call the dot product protocol k times to get an vector of k encrypted values. They can be done by sending a POST request to `http://127.0.0.1:8000/hyperplane_dot`.  
+ Once we get the result, we then call the argmax protocol to get the final class. We send a post request with the vector of k encrypted values and get `http://127.0.0.1:5000/argmax/vector_nokey`