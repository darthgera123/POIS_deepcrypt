from flask import Blueprint, Response, Flask, jsonify, render_template, request, url_for, redirect, flash, current_app
from POIS_deepcrypt.dgk import *
from POIS_deepcrypt.serverA.utils import *
import requests
from veu11_blueprint import veu11_compare_no_priv
from tqdm import tqdm

argmax_blueprint = Blueprint('argmax', __name__)

@argmax_blueprint.route("/init", methods=['GET', 'POST'])
def argmax_init():
	current_app.config['dgk_l'] = request.json['l']
	current_app.config["data"][ 'private_b_var' ] = 0

@argmax_blueprint.route("/request_index", methods=['GET', 'POST'])
def argmax_request_index():
	if not current_app.config['paillier_pub'] or not current_app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)
	if not current_app.config['gm_pub'] or not current_app.config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)
	return jsonify( bvar = current_app.config["data"]['private_b_var'] )

@argmax_blueprint.route("/compare", methods=['GET', 'POST'])
def argmax_compare():
	if not current_app.config['paillier_pub'] or not current_app.config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)
	if not current_app.config['gm_pub'] or not current_app.config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)

	qr_privk = current_app.config['gm_priv']
	pubk = current_app.config['paillier_pub']
	privk = current_app.config['paillier_priv']

	# cheat = deserialize(request.json['cheat'])
	# print(paillier.decrypt(cheat,privk),"CHEAT DEBUG SHUBHU")
		
	enc_bit = request.json['enc_bit'] 
	idx = request.json['idx'] 
	ai_rand =  deserialize( request.json['ai_rand'] )
	mx_rand =  deserialize( request.json['mx_rand'] )
	l =  request.json['l'] 

	isless = bool(gm.decrypt([enc_bit],qr_privk))

	if isless:
		current_app.config["data"]['private_b_var'] = idx
		print( idx , current_app.config["data"]['private_b_var']  , "DEBUG INDEX")
		vi = refresh_b( ai_rand , pubk , privk )
		bit_paillier = paillier.encrypt(1,pubk)
	else:	
		vi = refresh_b( mx_rand , pubk , privk )
		bit_paillier = paillier.encrypt(0,pubk)

	return jsonify( bi = serialize(bit_paillier) , vi = serialize(vi) )	

@argmax_blueprint.route("/vector_nokey", methods=['GET', 'POST'])
def argmax_vector_nokey():


	x = request.json['inp']["a1"]
	x = x.split(";")
	y = request.json['inp']["a2"]
	y = y.split(";")
	l = request.json['inp']["a3"]

	inp=[]

	current_app.config['dgk_l'] = l

	print(l)

	for i in range(len(x)):
		inp.append(paillier.PaillierCiphertext(mpz(x[i]),mpz(y[i])))

	inp=np.array(inp)
	perm=np.arange(0,inp.shape[0])
	shuf_inp = inp[ perm ]
	mxval = shuf_inp[ 0 ]

	requests.post("http://127.0.0.1:8000/argmax/init",json={"l":l})


	pubk = current_app.config["paillier_pub"]

	for i in tqdm(range(1,len(shuf_inp))):
		
		ai = shuf_inp[ i ]	
		
		current_app.config["data"]['veu11_operand1'] = mxval
		current_app.config["data"]['veu11_operand2'] = ai
		
		resp = (veu11_compare_no_priv())

		enc_bit , dec = resp.json['t'],resp.json['t_dec']

		print(dec,"DEBUG")

		r = random.getrandbits( l + 1 )
		s = random.getrandbits( l + 1 )
		
		enc_r = paillier.encrypt( r , pubk )
		enc_s = paillier.encrypt( s , pubk )

		mx_rand = mxval + enc_r
		ai_rand = ai + enc_s

		ret = requests.post("http://127.0.0.1:8000/argmax/compare", json={"mx_rand":serialize(mx_rand), "ai_rand":serialize(ai_rand),"l":l,"enc_bit":enc_bit,"idx":i,"cheat":serialize(mxval)})

		print( ret , "COMPARE REQUEST SENT" )
		bi , vi = deserialize(ret.json()['bi']),deserialize(ret.json()['vi'])
		one_enc = paillier.encrypt(mpz(1),pubk)

		remove_r = ( bi - one_enc ) * r
		remove_s = bi * s

		vi = vi + remove_r
		vi = vi - remove_s
		mxval = vi

	shuf_idx = requests.post("http://127.0.0.1:8000/argmax/request_index")
	ret = {"answer":str(perm[ shuf_idx.json()['bvar'] ])}	
	return jsonify(ans=ret)


# @argmax_blueprint.route("/vector_nokey", methods=['GET', 'POST'])
# def argmax_vector_nokey():

# 	global config,data

# 	x = request.json['inp']["a1"]
# 	x = x.split(";")
# 	y = request.json['inp']["a2"]
# 	y = y.split(";")
# 	l = request.json['inp']["a3"]

# 	inp=[]

# 	current_app.config['dgk_l'] = l

# 	print(l)

# 	for i in range(len(x)):
# 		inp.append(paillier.PaillierCiphertext(mpz(x[i]),mpz(y[i])))

# 	inp=np.array(inp)
# 	perm=np.arange(0,inp.shape[0])
# 	shuf_inp = inp[ perm ]
# 	mxval = shuf_inp[ 0 ]

# 	requests.post("http://127.0.0.1:8000/argmax/init",json={"l":l})


# 	pubk = current_app.config["paillier_pub"]

# 	for i in tqdm(range(1,len(shuf_inp))):
		
# 		ai = shuf_inp[ i ]	
		
# 		current_app.config["data"]['veu11_operand1'] = mxval
# 		current_app.config["data"]['veu11_operand2'] = ai
		
# 		resp = (veu11_compare_no_priv())

# 		enc_bit , dec = resp.json['t'],resp.json['t_dec']

# 		print(dec,"DEBUG")

# 		r = random.getrandbits( l + 1 )
# 		s = random.getrandbits( l + 1 )
		
# 		enc_r = paillier.encrypt( r , pubk )
# 		enc_s = paillier.encrypt( s , pubk )

# 		mx_rand = mxval + enc_r
# 		ai_rand = ai + enc_s

# 		ret = requests.post("http://127.0.0.1:8000/argmax/compare", json={"mx_rand":serialize(mx_rand), "ai_rand":serialize(ai_rand),"l":l,"enc_bit":enc_bit,"idx":i,"cheat":serialize(mxval)})

# 		print( ret , "COMPARE REQUEST SENT" )
# 		bi , vi = deserialize(ret.json()['bi']),deserialize(ret.json()['vi'])
# 		one_enc = paillier.encrypt(mpz(1),pubk)

# 		remove_r = ( bi - one_enc ) * r
# 		remove_s = bi * s

# 		vi = vi + remove_r
# 		vi = vi - remove_s
# 		mxval = vi

# 	shuf_idx = requests.post("http://127.0.0.1:8000/argmax/request_index")
# 	ret = {"answer":str(perm[ shuf_idx.json()['bvar'] ])}	
# 	return jsonify(ans=ret)