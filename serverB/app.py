"""
This hosts the model. The client server makes api calls by sending data to the model server
The model server here then responds to those POST requests
"""
# @app.route('/api/model/addition',methods = ['GET',"POST"])
# def api_addition():
# 	encrypt_key = random.randint(0,1e5)
# 	if request.method == 'GET':
# 		return jsonify(encrypt_key)
# 	if request.method == 'POST':
# 		number = request.json['number']
# 		new_number = int(number) + encrypt_key
# 		return jsonify(new_number)

# @app.route('/api/model/subtraction',methods = ["POST"])
# def api_subtraction():
# 	encrypt_key = random.randint(0,1e5)
# 	if request.method == 'POST':
# 		number = request.json['number']
# 		new_number = int(number) - encrypt_key
# 		return jsonify(new_number)

from flask import Response, Flask, jsonify, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename
from forms import DataForm
import requests
import dgk as dgk
import numpy as np
import sys
from sympy.core.numbers import mod_inverse
import random

def get_bits(n, l):
    bits = []
    for i in range(l):
        bits.append(n & 1)
        n = n >> 1
    return bits

app = Flask(__name__)
app.config["DEBUG"] = True
config = {
    'dgk_priv': None,
    'dgk_pub': None,
    'dgk_l': 4,
}
data = {
    'compare_operand': None,
}

############  DGK #########################

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
    data['compare_operand'] = request.json['val']
    return Response(status=200)

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

    response = requests.post("http://127.0.0.1:5000/dgk_compare_no_priv", json={
        'y_enc': y_enc
    })
    
    c, dela = response.json()

    delb = 0
    for ci in c:
        ci_iszero = dgk.decrypt_iszero(ci, config['dgk_priv'])
        if(ci_iszero):
            delb = 1
            break

    return jsonify(dela ^ delb)

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
        c.append(temp)
    # shuffle c 
    random.shuffle(c)

    return jsonify(c, dela)
######################## DGK compare #############################
# test commands:
# >>> requests.post("http://127.0.0.1:8000/dgk_init", json={'regen': False})
# >>> requests.post("http://127.0.0.1:8000/set_compare_operand", json={'val': 8})
# >>> requests.post("http://127.0.0.1:5000/set_compare_operand", json={'val': 5})
# >>> requests.post("http://127.0.0.1:8000/dgk_compare_has_priv")


# argv1 is the port number 
if __name__=='__main__':
    app.run(debug=True,port=sys.argv[1])
    
