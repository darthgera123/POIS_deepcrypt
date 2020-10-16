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

