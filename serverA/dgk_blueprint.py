from flask import Blueprint, Response, Flask, jsonify, render_template, request, url_for, redirect, flash, current_app
from POIS_deepcrypt.dgk import *
from POIS_deepcrypt.serverA.utils import *
import requests
dgk_blueprint = Blueprint('dgk', __name__)



@dgk_blueprint.route("/init", methods=['GET', 'POST'])
def dgk_init():
	regen = request.json['regen']
	if regen:
		current_app.config['dgk_priv'], current_app.config['dgk_pub'] = dgk.keygen(2048, 160, 18, "./")
	else:
		current_app.config['dgk_pub'] = np.load("./pub.npy", allow_pickle=True).item()
		current_app.config['dgk_priv'] = np.load("./priv.npy", allow_pickle=True).item()
	print("YAY")
	response = requests.post("http://127.0.0.1:5000/dgk/set_pub", json={
		'dgk_pub': current_app.config['dgk_pub']
	})

	if response.status_code != 200:
		print("Public Key sharing failed")

	return Response("", status=200)

@dgk_blueprint.route("/set_pub", methods=['GET', 'POST'])
def dgk_set_pub():	
	current_app.config['dgk_pub'] = request.json['dgk_pub']
	current_app.config['dgk_priv'] = None
	
	return Response("", status=200)

@dgk_blueprint.route('/encrypt', methods=['POST'])
def dgk_encrypt():	
	if not current_app.config['dgk_pub']:
		print("No public key available.")
		return Response("", status=404, mimetype='application/json')
	c = dgk.encrypt(request.json['m'], current_app.config['dgk_pub'])
	
	return jsonify(c)

@dgk_blueprint.route('/decrypt', methods=['GET', 'POST'])
def dgk_decrypt():
	if not current_app.config['dgk_priv']:
		print("No private key available.")
		return Response("", status=404, mimetype='application/json')

	m = dgk.decrypt_iszero(request.json['c'], current_app.config['dgk_priv'])
	if(m == 1):
		return jsonify(True)
	else:
		return jsonify(False)

@dgk_blueprint.route('/compare_has_priv', methods=['GET', 'POST'])
def dgk_compare_has_priv():
	if not current_app.config['dgk_priv']:
		print("Private Key not available for DGK.")
		return Response("", status=404)

	if not current_app.config["data"]['compare_operand']:
		print("Comparison operand not set.")
		return Response("", status=404)        

	# get bits
	y_b = get_bits(current_app.config["data"]['compare_operand'], current_app.config['dgk_l'])
	# get encrypted bits
	y_enc = []
	for b in y_b:
		y_enc.append(dgk.encrypt(b, current_app.config['dgk_pub']))

	response = requests.post("http://127.0.0.1:8000/dgk/compare_no_priv", json={
		'y_enc': y_enc
	})
	
	c, dela = response.json()

	delb = 0
	for ci in c:
		ci_iszero = dgk.decrypt_iszero(ci, current_app.config['dgk_priv'])
		if(ci_iszero):
			delb = 1
			break

	return jsonify(t=dela ^ delb)

@dgk_blueprint.route("/compare_no_priv", methods=['GET', 'POST'])
def dgk_compare_no_priv():
	if not current_app.config['dgk_pub'] or current_app.config['dgk_priv']:
		print("Key inconsistency for DGK.")
		return Response("", status=404)

	if not current_app.config["data"]['compare_operand']:
		print("Comparison operand not set.")
		return Response("", status=404)

	pub = current_app.config['dgk_pub']
	y_enc = request.json['y_enc']
	l = len(y_enc)

	# get encryption of 1
	one_enc = dgk.encrypt(1, pub)

	# get encryption of 0
	zero_enc = dgk.encrypt(0, pub)

	# get bits
	x_b = get_bits(current_app.config["data"]['compare_operand'], current_app.config['dgk_l'])
	# get encrypted bits
	x_enc = []
	for b in x_b:
		if b == 0:
			x_enc.append(zero_enc)
		else:
			x_enc.append(one_enc)
	x_enc = np.array(x_enc)

	# get [x xor y]
	xxory = []
	for i in range(l):
		if x_b[i] == 0:
			xxory.append(y_enc[i])
		else:
			xxory.append(
					(
					(one_enc%pub['n']) *
					(mod_inverse(y_enc[i], pub['n'])%pub['n'])
					)%pub['n']
				)
	xxory = np.array(xxory)

	dela = np.random.randint(0, 2)
	s = 1 - 2*dela
	s_enc = dgk.encrypt(s, pub)

	# precompute xor cubes
	xor3precomp = [1]*l
	i = l-2
	while(i >= 0):
		xor3precomp[i] = (
						(faster(xxory[i+1], 3, pub['n'])%pub['n']) *
						(xor3precomp[i+1]%pub['n'])
						)%pub['n']
		i -= 1
	xor3precomp = np.array(xor3precomp)


	# compute [c]
	c = []
	pubn, pubu, pubt, pubh = pub['n'], pub['u'], pub['t'], pub['h']
	# precomputed to save time
	dgk_rdash = np.load("r_dash.npy", allow_pickle=True)

	# temp_arr = (
	# 			(s_enc%pubn) *
	# 			(x_enc%pubn) *
	# 			(xor3precomp%pubn)
	# 			)%pubn
	for i in range(l):
		temp = (
				(s_enc%pubn) *
				(x_enc[i]%pubn) *
				(mod_inverse(y_enc[i], pubn))%pubn *
				(xor3precomp[i]%pubn)
				)%pubn
		# temp = (temp_arr[i] * (mod_inverse(y_enc[i], pubn))%pubn)%pubn

		r = np.random.randint(1, pubu)
		r_dash = random.getrandbits(int(2.5*pubt))

		temp = (
				faster(temp, r, pubn) *
				np.random.choice(dgk_rdash)
				# faster(pubh, r_dash, pubn)
			)%pubn
		c.append(int(temp))

	# shuffle c 
	random.shuffle(c)

	return jsonify(c, dela)