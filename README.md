# POIS_deepcrypt

### Requirements: Python3
- sympy
- numpy
- gensafeprime
- Flask
### Presentation Slides:
- Available in POISDeepcrypt.pdf
### Paillier Cryptosystem:
- Python library - paillierlib
- Usage:
-    Generating key pair - paillier.keygen()
-   encryption - paillier.encrypt(message, keypair.public_key)
-   decryption - paillier.decrypt(message, keypair.private_key)
-   Homomorphic operations - Use normal operations in the encrypted domain as well, it internally takes care of it.
-   Doc - https://pypi.org/project/paillierlib/
- We have created a faster version of paillierlib, we have named it as paillierlib, the corresponding folder is provided in our code.
- The slower version of paillierlib named as paillierlib2is present in the paillierlib2 folder.
- In order to import paillierlib and paillierlib2, just place the corresponding folders in the directory "/lib/python3.6/site-packages" present in your environment. (This location might be different based on where installation of libraries occurs on your system , you can find this path using `pip show numpy` (to get the installation location))

## IMPORTING FILES
- write these 2 lines in a script setup.py and save it in parent directory of POIS_deepcrypt
- line 1: from setuptools import setup, find_packages
- line 2: setup(name='myproject', version='1.0', packages=find_packages())
- run 'pip3 install -e .' in parent directory of POIS_deepcrypt	
- Use ' from POIS_deepcrypt.dir1.dir2 import file ' to import a file anywhere , then use file.function() 

## Hosting Servers
- In the serverA folder, run python3 app.py 5000, python3 app.py 5001, python3 app.py 8000
- Ports 5000 and 5001 are used by the client and port 8000 is used by server.

## HOW TO USE
### DGK Cryptosystem
- This cryptosystem is one of the foundational cryptosystems used in this product by a lot of the modules.
- The keys are setup by sending a POST request to the server which is supposed to hold the private key(8000) by calling `"http://127.0.0.1:8000/dgk_init"` which in turn distributes the public key to the other server(5000) by calling `"http://127.0.0.1:5000/dgk/set_pub"` and sending the public key through JSON.
- The encryption is done by sending a post request to the route as follows: `requests.post("http://127.0.0.1:5000/dgk_encrypt", json={'m': 123}).json()`.
- The decryption is done by sending a post request to the route on the server with the private key as follows: `requests.post("http://127.0.0.1:8000/dgk_decrypt", json={'c': c})`.
- Please refer the slides for additional theory for the implementation.

### Private Unencrypted Comparison
- This method of comparison is pretty fundamental, but it acts as a very important component of a lot of complex algorithms present in this product.
- We need to set up the DGK keys as discussed in the previous section before we can make use of this algorithm.
- Additionally we need to setup the operand for comparison on both the parties, which can be done in any way, one simple of which has been included in this product through the route of `http://[server ip: server port]/set_compare_operand`.
- Now we can call the route `http://127.0.0.1:8000/dgk_compare_has_priv` on the server with the DGK private key to initiate the comparison protocol which itself will initiate the steps on the other server in between the protocol by sending a request as follows: `requests.post("http://127.0.0.1:8000/dgk/compare_no_priv",json={'y_enc': y_enc})`.
- At the end of this protocol, both servers will hold a bit the XOR of which will give the final result. These bits are communicated based on the needs of the protocol built on top of this protocol.
- Please refer the slides for additional theory for the implementation.

### Veu11 Comparison Protocol
- The client (port 5000) has two encrypted numbers and the server (port 8000) has the private keys for paillier and goldwasser micali. Client gets the encrypted bit according to the result of the comparison.
- After the servers are hosted, run python3 test_veull.py to check output of protocol. In this file, random numbers are generated and comparison bit is received from the server. Currently we are also returning the decrypted bit for testing purpose.
- This protocol uses dgk comparison protocol to compute encrypted comparison bit for the comparison of two unencrypted numbers generated in the protocol. Each party has one unencrypted number.
- Refer to the contents of this file to check which requests are used to get the output.
- Refer to the presentation slides for details of the protocol.

### Dot Product Protocol
- The client (port 5000) has vector X and the server (port 8000) has the private keys for paillier and vector Y.
- The set_dot_product initialises and sends the encrypted vector Y to the client.
- The client then computes this encrypted dot product and sends to server.
- The server since it has the private key decrypts it.   
- Please refer the slides for additional theory and a diagram of the exchheanges and other details.


### Argmax Building block
- run "app.py <port number>" twice to represent a server runnning on a port and a client on the other.
- send a request to `http://127.0.0.1:<port nummber>/argmax_vector_nokey` , that port will not have secret key ,send just an encrypted vector ( client side).
- The function will internally run the argmax protocol with the server side which has the secret key.
- before calling the handler , some intitialization are to be performed , for underlying veu11 comparison protocol , "test_argmax.py" demonstrates that.
- The working is explained in the slides attached 
- "test_argmax.py" file demonstrates how above 4 steps are performed , run and study it to understand better.

### Hyperplane Classifier
Hyperplane classifier consists of the weights encrypted at the model server and the input with the keys at the client server. At the end we get the class to which the vector belongs.    
Send a POST request to `http://127.0.0.1:5000/hyperplane_handler` with the input vector.  
+ Internally it will call the dot product protocol k times to get an vector of k encrypted values. They can be done by sending a POST request to `http://127.0.0.1:8000/hyperplane_dot`.  
+ Once we get the result, we then call the argmax protocol to get the final class. We send a post request with the vector of k encrypted values and get `http://127.0.0.1:5000/argmax/vector_nokey`

### Naiive Bayes Classifier
- Run this after hosting the servers.
- The server side will require to send its encrypted model information and probability tables to the bayes_handler route of app.py .
- The server will send this encrypted info to the port 5000 which represents our client side. `http://127.0.0.1:5001/bayes_handler`
- This will internally do the bayes computation as shown in the slides and send argmax request to the handler `http://127.0.0.1:5000/argmax_vector_nokey` , 5000 and 5001 both represent client side.
- "test_bayes.py" file captures the way to implement these 4 steps . this file is basically a implementation which a handler on server's side should undertake to complete the protocol . 
