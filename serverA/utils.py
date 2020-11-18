from flask import current_app
import requests
from POIS_deepcrypt.dgk import *
import POIS_deepcrypt.goldwasser_micali as gm


def get_bits(n, l):
	bits = []
	for i in range(l):
		bits.append(n & 1)
		n = n >> 1
	return bits

def faster(x,y,md=None):
	if md == None:
		return pow(x, y)

	res = 1
	x = x%md
	while y > 0: 
		if y%2 != 0 : 
			res = (res*x)%md 
		y = int(y/2) 
		x = (x*x)%md

	return res

def dgk_init_without_route(regen):

	if regen:
		current_app.config['dgk_priv'], current_app.config['dgk_pub'] = dgk.keygen(2048, 160, 18, "./")
	else:
		current_app.config['dgk_pub'] = np.load("./pub.npy", allow_pickle=True).item()
		current_app.config['dgk_priv'] = np.load("./priv.npy", allow_pickle=True).item()

	response = requests.post("http://127.0.0.1:8000/dgk/set_pub", json={
		'dgk_pub': current_app.config['dgk_pub']
	})

def set_compare_operand_without_route(val):
	current_app.config["data"]['compare_operand'] = val


def dgk_compare_has_priv_without_route():
	print("In without route")
	if not current_app.config['dgk_priv']:
		print("Private Key not available for DGK.")
		return Response("", status=404)

	if not current_app.config["data"]['compare_operand']:
		print("Comparison operand not set.")
		return Response("", status=404)        

	pub = current_app.config['dgk_pub']
	# get encryption of 1
	one_enc = dgk.encrypt(1, pub)

	# get encryption of 0
	zero_enc = dgk.encrypt(0, pub)

	# get bits
	y_b = get_bits(current_app.config["data"]['compare_operand'], current_app.config['dgk_l'])
	# get encrypted bits
	y_enc = []
	for b in y_b:
		if b == 0:
			y_enc.append(zero_enc)
		else:
			y_enc.append(one_enc)

	response = requests.post("http://127.0.0.1:8000/dgk/compare_no_priv", json={
		'y_enc': y_enc
	})
	
	c, dela = response.json()
	c = [mpz(i) for i in c]

	delb = 0
	for ci in c:
		ci_iszero = dgk.decrypt_iszero(ci, current_app.config['dgk_priv'])
		if(ci_iszero):
			delb = 1
			break

	N, _ = current_app.config["gm_pub"]
	
	c1 = gm.encrypt(dela, current_app.config["gm_pub"])
	c2 = gm.encrypt(delb, current_app.config["gm_pub"])
	
	c1_bit = list(c1)[0]
	c2_bit = list(c2)[0]

	return ((c1_bit%N * c2_bit%N)%N)

def MSB(x, l):
	return bool(x & pow(2, l))


def deserialize_arr(obj):

	x = obj["a1"]
	x = x.split(";")
	y = obj["a2"]
	y = y.split(";")
	l = obj["a3"]

	inp=[]

	current_app.config['dgk_l'] = l


	for i in range(len(x)):
		inp.append(paillier.PaillierCiphertext(mpz(x[i]),mpz(y[i])))

	return np.array(inp),l	

def serializeArr( gg , l ): 
	s1=str(gg[0].c)
	s2=str(gg[0].n)
	for i in range(1,len(gg)):
		s1=s1+";"+str(gg[i].c)
		s2=s2+";"+str(gg[i].n)
	dic={"a1":s1,"a2":s2,"a3":l}
	return dic


def serialize(x):
	pn = int(x.n)
	pc = int(x.c)
	dic={"paillier_c":pc,"paillier_n":pn}
	return dic

def deserialize(x):
	y = paillier.PaillierCiphertext(x["paillier_c"],x["paillier_n"])
	return y

def refresh_b( num ,pubk , privk):

	plainval = paillier.decrypt( num , privk )
	re_enc = paillier.encrypt( plainval , pubk )
	return re_enc


def dot(a, b):
    fval = []
    for ind,each in enumerate(b):
	    c2 = mpz(a[ind])
	    c1 = each
	    x = c1*c2
	    fval.append(x)
    fsum = fval[0]
    for val in fval[1:]:
        fsum+=val
    return fsum 

def compute_dot(inp_vec, weights):
    encrypted_dot_product = []
    for i in range(len(weights)):
        output = dot(inp_vec, weights[i])
        encrypted_dot_product.append(output)
    return np.asarray(encrypted_dot_product)