# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# @app.route('/')
# def hello():
#     form = DataForm()
#     return render_template('hello.html', form=form)

# @app.route('/add', methods=['POST'])
# def add():
#     form = DataForm(request.form)
#     if request.method == 'POST' and form.validate():
#         response = requests.post("http://127.0.0.1:5000/api/model/addition", json={
#             'number': request.form['number']
#         })
#         if response.status_code == 200:
#             returned_data = response.json()
#             response1 = requests.post("http://127.0.0.1:5000/api/model/subtraction", json={
#                 'number': returned_data
#             })
#             if response1.status_code == 200:
#                 flash(response1.json())
#             else:
#                 flash("Issue in suctraction on server B")
#         else:
#             flash("Issue on Server B")
#     return redirect(url_for('hello'))
from flask import Response, Flask, jsonify, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename
# from forms import DataForm
import requests
from POIS_deepcrypt.dgk import *
import numpy as np
import sys
import random
import POIS_deepcrypt.goldwasser_micali as gm 
from gmpy2 import mpz
from paillierlib import paillier
from sympy.core.numbers import mod_inverse
import json
from tqdm import tqdm
def get_bits(n, l):
    bits = []
    for i in range(l):
        bits.append(n & 1)
        n = n >> 1
    return bits

def MSB(x, l):
    return bool(x & pow(2, l))

app = Flask(__name__)
app.config["DEBUG"] = True
config = {
    'dgk_priv': None,
    'dgk_pub': None,
    'dgk_l': 100,
    "paillier_priv" : None,
    "paillier_pub" : None,
    "gm_priv" : None,
    "gm_pub" : None,
}
data = {
    'compare_operand': None,
    'veu11_operand1':None,
    'veu11_operand2':None,
    'private_b_var':None,
}

############  DGK #########################

def dgk_init_without_route(regen):
    global config

    if regen:
        config['dgk_priv'], config['dgk_pub'] = dgk.keygen(2048, 160, 18, "./")
    else:
        config['dgk_pub'] = np.load("./pub.npy", allow_pickle=True).item()
        config['dgk_priv'] = np.load("./priv.npy", allow_pickle=True).item()

    response = requests.post("http://127.0.0.1:8000/dgk_set_pub", json={
        'dgk_pub': config['dgk_pub']
    })

@app.route('/dgk_init', methods=['GET', 'POST'])
def dgk_init():
    global config
    regen = request.json['regen']
    if regen:
        config['dgk_priv'], config['dgk_pub'] = dgk.keygen(2048, 160, 18, "./")
    else:
        config['dgk_pub'] = np.load("./pub.npy", allow_pickle=True).item()
        config['dgk_priv'] = np.load("./priv.npy", allow_pickle=True).item()

    response = requests.post("http://127.0.0.1:5000/dgk_set_pub", json={
        'dgk_pub': config['dgk_pub']
    })

    if response.status_code != 200:
        print("Public Key sharing failed")

    return Response("", status=200)


@app.route('/dgk_set_pub', methods=['POST'])
def dgk_set_pub():
    global config
    
    config['dgk_pub'] = request.json['dgk_pub']
    config['dgk_priv'] = None
    
    return Response("", status=200)

@app.route('/dgk_encrypt', methods=['POST'])
def dgk_encrypt():
    global config
    
    if not config['dgk_pub']:
        print("No public key available.")
        return Response("", status=404, mimetype='application/json')
    c = dgk.encrypt(request.json['m'], config['dgk_pub'])
    
    return jsonify(c)


@app.route('/dgk_decrypt', methods=['GET', 'POST'])
def dgk_decrypt():
    global config
    if not config['dgk_priv']:
        print("No private key available.")
        return Response("", status=404, mimetype='application/json')

    m = dgk.decrypt_iszero(request.json['c'], config['dgk_priv'])
    if(m == 1):
        return jsonify(True)
    else:
        return jsonify(False)

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
    data['compare_operand'] = request.json["val"]
    return Response(status=200)

def set_compare_operand_without_route(val):
    global data
    data['compare_operand'] = val


# this is the party with the private key
# as of now the other party will return the unencrypted del value to this party
@app.route('/dgk_compare_has_priv', methods=['GET', 'POST'])
def dgk_compare_has_priv():
    global config, data
    if not config['dgk_priv']:
        print("Private Key not available for DGK.")
        return Response("", status=404)

    if not data['compare_operand']:
        print("Comparison operand not set.")
        return Response("", status=404)        

    # get bits
    y_b = get_bits(data['compare_operand'], config['dgk_l'])
    # get encrypted bits
    y_enc = []
    for b in y_b:
        y_enc.append(dgk.encrypt(b, config['dgk_pub']))

    response = requests.post("http://127.0.0.1:8000/dgk_compare_no_priv", json={
        'y_enc': y_enc
    })
    
    c, dela = response.json()

    delb = 0
    for ci in c:
        ci_iszero = dgk.decrypt_iszero(ci, config['dgk_priv'])
        if(ci_iszero):
            delb = 1
            break

    return jsonify(t=dela ^ delb)


# this is the party without the private key
# this will send its unencrypted del value to the other party
@app.route("/dgk_compare_no_priv", methods=['GET', 'POST'])
def dgk_compare_no_priv():
    global config, data

    if not config['dgk_pub'] or config['dgk_priv']:
        print("Key inconsistency for DGK.")
        return Response("", status=404)

    if not data['compare_operand']:
        print("Comparison operand not set.")
        return Response("", status=404)

    pub = config['dgk_pub']
    y_enc = request.json['y_enc']
    l = len(y_enc)

    # get bits
    x_b = get_bits(data['compare_operand'], config['dgk_l'])
    # get encrypted bits
    x_enc = []
    for b in x_b:
        x_enc.append(dgk.encrypt(b, pub))
    x_enc = np.array(x_enc)
    # get encryption of 1
    one_enc = dgk.encrypt(1, pub)
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
                        (pow(xxory[i+1], 3, pub['n'])%pub['n']) *
                        (xor3precomp[i+1]%pub['n'])
                        )%pub['n']
        i -= 1
    # compute [c]
    c = []
    for i in range(l):
        temp = (
                (s_enc%pub['n']) *
                (x_enc[i]%pub['n']) *
                (mod_inverse(y_enc[i], pub['n']))%pub['n'] *
                (xor3precomp[i]%pub['n'])
                )%pub['n']
        r = np.random.randint(1, pub['u'])
        r_dash = random.getrandbits(int(2.5*pub['t']))
        temp = (
                pow(temp, r, pub['n']) *
                pow(pub['h'], r_dash, pub['n'])
            )%pub['n']
        c.append(int(temp))
    # shuffle c 
    random.shuffle(c)
    return jsonify(c, dela)

def dgk_compare_has_priv_without_route():
    global config, data

    if not config['dgk_priv']:
        print("Private Key not available for DGK.")
        return Response("", status=404)

    if not data['compare_operand']:
        print("Comparison operand not set.")
        return Response("", status=404)        

    # get bits
    y_b = get_bits(data['compare_operand'], config['dgk_l'])
    # get encrypted bits
    y_enc = []
    for b in y_b:
        y_enc.append(dgk.encrypt(b, config['dgk_pub']))

    response = requests.post("http://127.0.0.1:8000/dgk_compare_no_priv", json={
        'y_enc': y_enc
    })
    
    c, dela = response.json()
    c = [mpz(i) for i in c]

    delb = 0
    for ci in c:
        ci_iszero = dgk.decrypt_iszero(ci, config['dgk_priv'])
        if(ci_iszero):
            delb = 1
            break

    N, _ = config["gm_pub"]
    
    c1 = gm.encrypt(dela, config["gm_pub"])
    c2 = gm.encrypt(delb, config["gm_pub"])
    # one = gm.encrypt(1, config["gm_pub"])
    
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
    key_pair = np.load("./PAILLIER_KEY.npy")[0]
    gm_key_pair = np.load("./GM_KEY.npy")[0]

    config["paillier_priv"] = key_pair.private_key
    config["paillier_pub"] = key_pair.public_key
    config["gm_priv"] = gm_key_pair["priv"]
    config["gm_pub"] = gm_key_pair["pub"]

    public_key = {"n":int(key_pair.public_key.n), "g":int(key_pair.public_key.g)}

    response = requests.post("http://127.0.0.1:5000/veu11_set_pub", json={
        'paillier_pub': public_key,
        'gm_pub': config["gm_pub"],
    })
    if response.status_code != 200:
        print("Public Key sharing failed")

        
    return Response("", status=200)
    
@app.route('/veu11_set_pub', methods=['POST'])
def veu11_set_pub():
    global config
    public_key = request.json["paillier_pub"]

    config['paillier_pub'] = paillier.PaillierPublicKey(n=mpz(public_key["n"]), g=int(public_key["g"]))
    config['gm_pub'] = request.json['gm_pub']   
    config['paillier_priv'] = None
    config['gm_priv'] = None
    
    return Response("", status=200)

@app.route("/veu11_compare_no_priv", methods=['GET', 'POST'])
def veu11_compare_no_priv():

    global config, data

    if not config['paillier_pub'] or config['paillier_priv']:
        print("Key inconsistency for Veu11.")
        return Response("", status=404)

    if not config['gm_pub'] or config['gm_priv']:
        print("Key inconsistency for Goldwasser Micali.")
        return Response("", status=404)

    if not data['veu11_operand1'] or not data["veu11_operand2"]:
        print("Comparison operands not set for Veu11.")
        return Response("", status=404)

    encrypted_a = data["veu11_operand1"]
    encrypted_b = data["veu11_operand2"]
    l = config['dgk_l']

    x = encrypted_b + paillier.encrypt(mpz(pow(2, l)), config["paillier_pub"]) - encrypted_a
    r = random.getrandbits(l + 2)
    z = x + paillier.encrypt(mpz(r), config["paillier_pub"])
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
        r_l = gm.encrypt(1, config["gm_pub"])
    else:
        r_l = gm.encrypt(0, config["gm_pub"])

    N, _ = config["gm_pub"]
    t_ = (z_l[0]%N * r_l[0]%N)%N
    t = (t_%N * t%N)%N

    response = requests.post("http://127.0.0.1:8000/print_t", json={"t":t})
    return jsonify(t=t, t_dec=response.json()["t_dec"])

@app.route("/print_t", methods=['GET', 'POST'])
def print_t():
    t = request.json["t"]
    return jsonify(t_dec=gm.decrypt([t], config["gm_priv"]))

@app.route("/veu11_compare_has_priv", methods=['GET', 'POST'])
def veu11_compare_has_priv():
    global config, data

    if not config['paillier_priv']:
        print("Key inconsistency for Veu11.")
        return Response("", status=404)

    if not config['gm_priv']:
        print("Key inconsistency for Goldwasser Micali.")
        return Response("", status=404)

    z = paillier.PaillierCiphertext(c=mpz(request.json["z"]["c"]), n=mpz(request.json["z"]["n"]))

    z_dec = paillier.decrypt(z, config["paillier_priv"])
    d = z_dec % pow(2, config["dgk_l"])

    set_compare_operand_without_route(d) 

    if MSB(z_dec, config["dgk_l"]):
        z_l = gm.encrypt(1, config["gm_pub"])
    else:
        z_l = gm.encrypt(0, config["gm_pub"])

    return jsonify(z_l=z_l)

@app.route("/set_veu11_operands", methods=['GET', 'POST'])
def set_veu11_operands():

    if config["paillier_priv"] or config["gm_priv"]:
        print("Key inconsistency")
        return Response("", status=404) 

    global data

    data['veu11_operand1'] = paillier.encrypt(mpz(request.json['val1']), config["paillier_pub"])
    data['veu11_operand2'] = paillier.encrypt(mpz(request.json['val2']), config["paillier_pub"])
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
	config['dgk_l']=request.json['l']
	data[ 'private_b_var' ]= 0

@app.route("/argmax_request_index", methods=['GET', 'POST'])
def argmax_request_index():
	global config, data
	if not config['paillier_pub'] or not config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)
	if not config['gm_pub'] or not config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)
	return jsonify( bvar = data['private_b_var'] )

@app.route("/argmax_compare", methods=['GET', 'POST'])
def argmax_compare():
	global config, data
	if not config['paillier_pub'] or not config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)
	if not config['gm_pub'] or not config['gm_priv']:
		print("Key inconsistency for Goldwasser Micali.")
		return Response("", status=404)

	qr_privk = config['gm_priv']
	pubk = config['paillier_pub']
	privk = config['paillier_priv']

	# cheat = deserialize(request.json['cheat'])
	# print(paillier.decrypt(cheat,privk),"CHEAT DEBUG SHUBHU")
		
	enc_bit = request.json['enc_bit'] 
	idx = request.json['idx'] 
	ai_rand =  deserialize( request.json['ai_rand'] )
	mx_rand =  deserialize( request.json['mx_rand'] )
	l =  request.json['l'] 

	isless = bool(gm.decrypt([enc_bit],qr_privk))

	if isless:
		data['private_b_var'] = idx
		print( idx , data['private_b_var']  , "DEBUG INDEX")
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

	config['dgk_l'] = l

	print(l)

	for i in range(len(x)):
		inp.append(paillier.PaillierCiphertext(mpz(x[i]),mpz(y[i])))

	inp=np.array(inp)
	perm=np.arange(0,inp.shape[0])
	shuf_inp = inp[ perm ]
	mxval = shuf_inp[ 0 ]

	requests.post("http://127.0.0.1:8000/argmax_init",json={"l":l})

	pubk = config["paillier_pub"]

	for i in tqdm(range(1,len(shuf_inp))):
		
		ai = shuf_inp[ i ]	
		
		data['veu11_operand1'] = mxval
		data['veu11_operand2'] = ai
		
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
	if not config['paillier_pub'] or config['paillier_priv']:
		print("Key inconsistency for Veu11.")
		return Response("", status=404)

	spk = {"n":str(config['paillier_pub'].n), "g":str(config['paillier_pub'].g)}	
	return jsonify(pbk=spk)    	

def deserialize_arr(obj):

	x = obj["a1"]
	x = x.split(";")
	y = obj["a2"]
	y = y.split(";")
	l = obj["a3"]

	inp=[]

	config['dgk_l'] = l


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

	DATA = np.load("./DATA.npy")
	LABEL = np.load("./LABEL.npy")

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

if __name__=='__main__':
    app.run(debug=True,port=int(sys.argv[1]))
    
