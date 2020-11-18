import json
import random
import sys
import time

import numpy as np
import POIS_deepcrypt.goldwasser_micali as gm
import requests
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)
from gmpy2 import mpz
from paillierlib import paillier
from POIS_deepcrypt.dgk import *
from POIS_deepcrypt.serverA.utils import *
from sympy.core.numbers import mod_inverse
from tqdm import tqdm
from werkzeug.utils import secure_filename

from dgk_blueprint import dgk_blueprint

def MSB(x, l):
	return bool(x & pow(2, l))

app = Flask(__name__)
app.register_blueprint(dgk_blueprint, url_prefix="/dgk")

app.config["DEBUG"] = True
# app.config = {
app.config['dgk_priv'] = None
app.config['dgk_pub'] = None
app.config['dgk_l'] = 100
app.config["paillier_priv"] = None
app.config["paillier_pub"] = None
app.config["gm_priv"] = None
app.config["gm_pub"] = None

# }
app.config["data"] = {
	'compare_operand': None,
	'veu11_operand1':None,
	'veu11_operand2':None,
	'private_b_var':None,
}

############  DGK #########################

def dgk_init_without_route(regen):
	global config

	if regen:
		app.config['dgk_priv'], app.config['dgk_pub'] = dgk.keygen(2048, 160, 18, "./")
	else:
		app.config['dgk_pub'] = np.load("./pub.npy", allow_pickle=True).item()
		app.config['dgk_priv'] = np.load("./priv.npy", allow_pickle=True).item()

	response = requests.post("http://127.0.0.1:8000/dgk/set_pub", json={
		'dgk_pub': app.config['dgk_pub']
	})

############  DGK #########################
#test commands: 
# requests.post("http://127.0.0.1:8000/dgk_init", json={'regen': False})
# c = requests.post("http://127.0.0.1:5000/dgk_encrypt", json={'m': 123}).json()
# m = requests.post("http://127.0.0.1:8000/dgk_decrypt", json={'c': c})



#################  DGK Compare ###############################
# for now the compare operands are set using the following function as no other function is there to call this procedure
@app.route("/set_compare_operand", methods=['GET', 'POST'])
def set_compare_operand():
	global data
	app.config["data"]['compare_operand'] = request.json["val"]
	return Response(status=200)

def set_compare_operand_without_route(val):
	global data
	app.config["data"]['compare_operand'] = val


def dgk_compare_has_priv_without_route():
	print("In without route")
	# global config, data
	# print(app.config)
	if not app.config['dgk_priv']:
		print("Private Key not available for DGK.")
		return Response("", status=404)

	if not app.config["data"]['compare_operand']:
		print("Comparison operand not set.")
		return Response("", status=404)        

	pub = app.config['dgk_pub']
	# get encryption of 1
	one_enc = dgk.encrypt(1, pub)

	# get encryption of 0
	zero_enc = dgk.encrypt(0, pub)

	# get bits
	y_b = get_bits(app.config["data"]['compare_operand'], app.config['dgk_l'])
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
		ci_iszero = dgk.decrypt_iszero(ci, app.config['dgk_priv'])
		if(ci_iszero):
			delb = 1
			break

	N, _ = app.config["gm_pub"]
	
	c1 = gm.encrypt(dela, app.config["gm_pub"])
	c2 = gm.encrypt(delb, app.config["gm_pub"])
	# one = gm.encrypt(1, app.config["gm_pub"])
	
	c1_bit = list(c1)[0]
	c2_bit = list(c2)[0]
	# one_bit = list(one)[0]

	return ((c1_bit%N * c2_bit%N)%N)

######################## DGK compare #############################
# test commands:
# >>> requests.post("http://127.0.0.1:8000/dgk_init", json={'regen': False})
# >>> requests.post("http://127.0.0.1:8000/set_compare_operand", json={'val': 8})
# >>> requests.post("http://127.0.0.1:5000/set_compare_operand", json={'val': 5})
# >>> requests.post("http://127.0.0.1:8000/dgk_compare_has_priv")

######################## Veu11 compare #############################

@app.route('/veu11_init', methods=['GET', 'POST'])
def veu11_init():
	global config
	key_pair = np.load("./PAILLIER_KEY.npy", allow_pickle=True)[0]
	gm_key_pair = np.load("./GM_KEY.npy", allow_pickle=True)[0]

	app.config["paillier_priv"] = key_pair.private_key
	app.config["paillier_pub"] = key_pair.public_key
	app.config["gm_priv"] = gm_key_pair["priv"]
	app.config["gm_pub"] = gm_key_pair["pub"]

	public_key = {"n":int(key_pair.public_key.n), "g":int(key_pair.public_key.g)}

	response = requests.post("http://127.0.0.1:5000/veu11_set_pub", json={
		'paillier_pub': public_key,
		'gm_pub': app.config["gm_pub"],
	})
	if response.status_code != 200:
		print("Public Key sharing failed")
		
	return Response("", status=200)
	
@app.route('/veu11_set_pub', methods=['POST'])
def veu11_set_pub():
	global config
	public_key = request.json["paillier_pub"]

	app.config['paillier_pub'] = paillier.PaillierPublicKey(n=mpz(public_key["n"]), g=int(public_key["g"]))
	app.config['gm_pub'] = request.json['gm_pub']   
	app.config['paillier_priv'] = None
	app.config['gm_priv'] = None
	
	return Response("", status=200)

@app.route("/veu11_compare_no_priv", methods=['GET', 'POST'])
def veu11_compare_no_priv():

	global config, data

	if not app.config['paillier_pub'] or app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)

	if not app.config['gm_pub'] or app.config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)

	if not app.config["data"]['veu11_operand1'] or not app.config["data"]["veu11_operand2"]:
		print("Comparison operands not set for Veu11.")
		return Response("", status=404)

	encrypted_a = app.config["data"]["veu11_operand1"]
	encrypted_b = app.config["data"]["veu11_operand2"]
	l = app.config['dgk_l']

	x = encrypted_b + paillier.encrypt(mpz(pow(2, l)), app.config["paillier_pub"]) - encrypted_a
	r = random.getrandbits(l + 2)
	z = x + paillier.encrypt(mpz(r), app.config["paillier_pub"])
	c = r % pow(2, l)

	encrypted_z = {
		"c" : int(z.c),
		"n" : int(z.n),
	}

	dgk_init_without_route(False)
	set_compare_operand_without_route(c)

	response = requests.post("http://127.0.0.1:8000/veu11_compare_has_priv", json={
		"z" : encrypted_z,   
	})
	
	z_l = response.json()["z_l"]
	
	t = dgk_compare_has_priv_without_route()

	if MSB(r, l):
		r_l = gm.encrypt(1, app.config["gm_pub"])
	else:
		r_l = gm.encrypt(0, app.config["gm_pub"])

	N, _ = app.config["gm_pub"]
	t_ = (z_l[0]%N * r_l[0]%N)%N
	t = (t_%N * t%N)%N

	response = requests.post("http://127.0.0.1:8000/print_t", json={"t":t})
	return jsonify(t=t, t_dec=response.json()["t_dec"])

@app.route("/print_t", methods=['GET', 'POST'])
def print_t():
	t = request.json["t"]
	return jsonify(t_dec=gm.decrypt([t], app.config["gm_priv"]))

@app.route("/veu11_compare_has_priv", methods=['GET', 'POST'])
def veu11_compare_has_priv():
	if not app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)

	if not app.config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)

	z = paillier.PaillierCiphertext(c=mpz(request.json["z"]["c"]), n=mpz(request.json["z"]["n"]))

	z_dec = paillier.decrypt(z, app.config["paillier_priv"])
	d = z_dec % pow(2, app.config["dgk_l"])

	set_compare_operand_without_route(d) 

	if MSB(z_dec, app.config["dgk_l"]):
		z_l = gm.encrypt(1, app.config["gm_pub"])
	else:
		z_l = gm.encrypt(0, app.config["gm_pub"])

	return jsonify(z_l=z_l)

@app.route("/set_veu11_operands", methods=['GET', 'POST'])
def set_veu11_operands():

	if app.config["paillier_priv"] or app.config["gm_priv"]:
		print("Key inconsistency")
		return Response("", status=404) 

	global data

	app.config["data"]['veu11_operand1'] = paillier.encrypt(mpz(request.json['val1']), app.config["paillier_pub"])
	app.config["data"]['veu11_operand2'] = paillier.encrypt(mpz(request.json['val2']), app.config["paillier_pub"])
	return Response(status=200)


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

@app.route("/argmax_init", methods=['GET', 'POST'])
def argmax_init():
	global data,config
	app.config['dgk_l']=request.json['l']
	app.config["data"][ 'private_b_var' ]= 0

@app.route("/argmax_request_index", methods=['GET', 'POST'])
def argmax_request_index():
	global config, data
	if not app.config['paillier_pub'] or not app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)
	if not app.config['gm_pub'] or not app.config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)
	return jsonify( bvar = app.config["data"]['private_b_var'] )

@app.route("/argmax_compare", methods=['GET', 'POST'])
def argmax_compare():
	global config, data
	if not app.config['paillier_pub'] or not app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)
	if not app.config['gm_pub'] or not app.config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)

	qr_privk = app.config['gm_priv']
	pubk = app.config['paillier_pub']
	privk = app.config['paillier_priv']

	# cheat = deserialize(request.json['cheat'])
	# print(paillier.decrypt(cheat,privk),"CHEAT DEBUG SHUBHU")
		
	enc_bit = request.json['enc_bit'] 
	idx = request.json['idx'] 
	ai_rand =  deserialize( request.json['ai_rand'] )
	mx_rand =  deserialize( request.json['mx_rand'] )
	l =  request.json['l'] 

	isless = bool(gm.decrypt([enc_bit],qr_privk))

	if isless:
		app.config["data"]['private_b_var'] = idx
		print( idx , app.config["data"]['private_b_var']  , "DEBUG INDEX")
		vi = refresh_b( ai_rand , pubk , privk )
		bit_paillier = paillier.encrypt(1,pubk)
	else:	
		vi = refresh_b( mx_rand , pubk , privk )
		bit_paillier = paillier.encrypt(0,pubk)

	return jsonify( bi = serialize(bit_paillier) , vi = serialize(vi) )	

	

@app.route("/argmax_vector_nokey", methods=['GET', 'POST'])
def argmax_vector_nokey():

	global config,data

	x = request.json['inp']["a1"]
	x = x.split(";")
	y = request.json['inp']["a2"]
	y = y.split(";")
	l = request.json['inp']["a3"]

	inp=[]

	app.config['dgk_l'] = l

	print(l)

	for i in range(len(x)):
		inp.append(paillier.PaillierCiphertext(mpz(x[i]),mpz(y[i])))

	inp=np.array(inp)
	perm=np.arange(0,inp.shape[0])
	shuf_inp = inp[ perm ]
	mxval = shuf_inp[ 0 ]

	requests.post("http://127.0.0.1:8000/argmax_init",json={"l":l})


	pubk = app.config["paillier_pub"]

	for i in tqdm(range(1,len(shuf_inp))):
		
		ai = shuf_inp[ i ]	
		
		app.config["data"]['veu11_operand1'] = mxval
		app.config["data"]['veu11_operand2'] = ai
		
		resp = (veu11_compare_no_priv())

		enc_bit , dec = resp.json['t'],resp.json['t_dec']

		print(dec,"DEBUG")

		r = random.getrandbits( l + 1 )
		s = random.getrandbits( l + 1 )
		
		enc_r = paillier.encrypt( r , pubk )
		enc_s = paillier.encrypt( s , pubk )

		mx_rand = mxval + enc_r
		ai_rand = ai + enc_s

		ret = requests.post("http://127.0.0.1:8000/argmax_compare", json={"mx_rand":serialize(mx_rand), "ai_rand":serialize(ai_rand),"l":l,"enc_bit":enc_bit,"idx":i,"cheat":serialize(mxval)})

		print( ret , "COMPARE REQUEST SENT" )
		bi , vi = deserialize(ret.json()['bi']),deserialize(ret.json()['vi'])
		one_enc = paillier.encrypt(mpz(1),pubk)

		remove_r = ( bi - one_enc ) * r
		remove_s = bi * s

		vi = vi + remove_r
		vi = vi - remove_s
		mxval = vi

	shuf_idx = requests.post("http://127.0.0.1:8000/argmax_request_index")
	ret = {"answer":str(perm[ shuf_idx.json()['bvar'] ])}	
	return jsonify(ans=ret)

@app.route("/share_public_key", methods=['GET', 'POST'])
def share_public_key():
	global config
	if not app.config['paillier_pub'] or app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)

	spk = {"n":str(app.config['paillier_pub'].n), "g":str(app.config['paillier_pub'].g)}	
	return jsonify(pbk=spk)    	

def deserialize_arr(obj):

	x = obj["a1"]
	x = x.split(";")
	y = obj["a2"]
	y = y.split(";")
	l = obj["a3"]

	inp=[]

	app.config['dgk_l'] = l


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

@app.route("/bayes_handler", methods=['GET', 'POST'])
def bayes_handler():

	DATA = np.load("./DATA.npy", allow_pickle=True)
	LABEL = np.load("./LABEL.npy", allow_pickle=True)

	clp,l = deserialize_arr(request.json['clp'])
	
	ret,l = deserialize_arr(request.json['cop'])

	sx,sy,sz=int(request.json['sx']),int(request.json['sy']),int(request.json['sz'])
	cop = ret.reshape(sx,sy,sz)

	correct , total = 0 , LABEL.shape[0]

	for i in range(total):
		
		inp_vec = DATA[ i ]

		class_posterior_list = []

		for class_index in range( cop.shape[0] ):

			class_prob = clp[ class_index ]
			probabilities = cop[ class_index ][ np.arange(cop.shape[1]) , inp_vec ]  
			class_prob = class_prob + np.sum(probabilities)
			class_posterior_list.append(class_prob)	

		class_posterior_list = np.array( class_posterior_list )
		
		getans = requests.post("http://127.0.0.1:5000/argmax_vector_nokey", json={"inp":serializeArr( class_posterior_list , l )})
		idx = int(getans.json()['ans']["answer"])

		if idx == LABEL[i]:
			correct+=1

	
	return jsonify(correct=str(correct),tot=str(total))

# @app.route('/dot_unenc', methods=['GET', 'POST'])
# def dot_unenc():
#     global config,data
        
#     c_value = request.json['val1']
#     n_value = request.json['val2']

#     dic={"paillier_c":c_value,"paillier_n":n_value}
#     data = deserialize(dic)

#     unenc = (int)(paillier2.decrypt(data, app.config["paillier_priv"] ))
#     return jsonify(unenc=unenc)

# @app.route("/set_dot_product", methods=['GET', 'POST'])
# def set_dot_product():
#     global config, data
#     # print(data, config)
#     pub = app.config['paillier_pub']
#     vector_b_encrypt = []
#     mdata = request.json['val2']

#     for each in mdata:
#         c1 = paillier2.encrypt(each, pub)
#         vector_b_encrypt.append(c1)


#     data['unenc_a'] = request.json['val1']
#     data['enc_b'] = vector_b_encrypt
#     print(data)
#     return Response(status=200)

# @app.route("/compute_dot", methods=['GET', 'POST'])
# def compute_dot():
#     global config,data

#     vector_b_encrypt = data['enc_b']
#     vector_a_unencrypt = data['unenc_a']
#     fval = paillier2.encrypt(0, app.config["paillier_pub"])
#     for ind,each in enumerate(vector_b_encrypt):
#         c2 = mpz(vector_a_unencrypt[ind])
#         c1 = each
#         x = c1 * c2
#         fval += x
#     w = serialize(fval)
#     return jsonify(fval=w)

@app.route("/hyperplane_dot", methods=['GET', 'POST'])
def compute_hyperplane_dot():
    encrypted_weights = np.load("./encrypted_weights.npy", allow_pickle=True)
    vector = request.json["vector"]

    dot = compute_dot(vector,encrypted_weights)

    return jsonify(serializeArr(dot, 30))
        


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


@app.route("/hyperplane_handler", methods=['GET', 'POST'])
def hyperplane_handler():
    input_vec = request.json["vector"]
    response = requests.post("http://127.0.0.1:8000/hyperplane_dot", json={
        "vector" : input_vec
    })
    vals, l = deserialize_arr(response.json())
    requests.post("http://127.0.0.1:8000/veu11_init")
    getans = requests.post(
        "http://127.0.0.1:5000/argmax_vector_nokey", 
        json={
            "inp":serializeArr( vals , 30 )
            }
        )

    return getans.json()

if __name__=='__main__':
	app.run(debug=True,port=int(sys.argv[1]))
	
