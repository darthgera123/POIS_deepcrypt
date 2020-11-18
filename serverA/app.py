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
from veu11_blueprint import veu11_blueprint, veu11_compare_no_priv
from argmax_blueprint import argmax_blueprint

app = Flask(__name__)
app.register_blueprint(dgk_blueprint, url_prefix="/dgk")
app.register_blueprint(veu11_blueprint, url_prefix="/veu11")
app.register_blueprint(argmax_blueprint, url_prefix="/argmax")
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
    'veu11_operand1': None,
    'veu11_operand2': None,
    'private_b_var': None,
}

############  DGK #########################


############  DGK #########################
# test commands:
# requests.post("http://127.0.0.1:8000/dgk_init", json={'regen': False})
# c = requests.post("http://127.0.0.1:5000/dgk_encrypt", json={'m': 123}).json()
# m = requests.post("http://127.0.0.1:8000/dgk_decrypt", json={'c': c})


#################  DGK Compare ###############################
# for now the compare operands are set using the following function as no
# other function is there to call this procedure
@app.route("/set_compare_operand", methods=['GET', 'POST'])
def set_compare_operand():
    global data
    app.config["data"]['compare_operand'] = request.json["val"]
    return Response(status=200)

######################## DGK compare #############################
# test commands:
# >>> requests.post("http://127.0.0.1:8000/dgk_init", json={'regen': False})
# >>> requests.post("http://127.0.0.1:8000/set_compare_operand", json={'val': 8})
# >>> requests.post("http://127.0.0.1:5000/set_compare_operand", json={'val': 5})
# >>> requests.post("http://127.0.0.1:8000/dgk_compare_has_priv")

######################## Veu11 compare #############################


@app.route("/print_t", methods=['GET', 'POST'])
def print_t():
    t = request.json["t"]
    return jsonify(t_dec=gm.decrypt([t], app.config["gm_priv"]))


@app.route("/set_veu11_operands", methods=['GET', 'POST'])
def set_veu11_operands():

    if app.config["paillier_priv"] or app.config["gm_priv"]:
        print("Key inconsistency")
        return Response("", status=404)

    app.config["data"]['veu11_operand1'] = paillier.encrypt(
        mpz(request.json['val1']), app.config["paillier_pub"])
    app.config["data"]['veu11_operand2'] = paillier.encrypt(
        mpz(request.json['val2']), app.config["paillier_pub"])
    return Response(status=200)


@app.route("/share_public_key", methods=['GET', 'POST'])
def share_public_key():
    global config
    if not app.config['paillier_pub'] or app.config['paillier_priv']:
        print("Key inconsistency for Veu11.")
        return Response("", status=404)

    spk = {
        "n": str(
            app.config['paillier_pub'].n), "g": str(
            app.config['paillier_pub'].g)}
    return jsonify(pbk=spk)


@app.route("/bayes_handler", methods=['GET', 'POST'])
def bayes_handler():

    DATA = np.load("./DATA.npy", allow_pickle=True)
    LABEL = np.load("./LABEL.npy", allow_pickle=True)

    clp, l = deserialize_arr(request.json['clp'])

    ret, l = deserialize_arr(request.json['cop'])

    sx, sy, sz = int(
        request.json['sx']), int(
        request.json['sy']), int(
            request.json['sz'])
    cop = ret.reshape(sx, sy, sz)

    correct, total = 0, LABEL.shape[0]

    for i in range(total):

        inp_vec = DATA[i]

        class_posterior_list = []

        for class_index in range(cop.shape[0]):

            class_prob = clp[class_index]
            probabilities = cop[class_index][np.arange(cop.shape[1]), inp_vec]
            class_prob = class_prob + np.sum(probabilities)
            class_posterior_list.append(class_prob)

        class_posterior_list = np.array(class_posterior_list)

        getans = requests.post(
            "http://127.0.0.1:5000/argmax/vector_nokey",
            json={
                "inp": serializeArr(
                    class_posterior_list,
                    l)})
        idx = int(getans.json()['ans']["answer"])

        if idx == LABEL[i]:
            correct += 1

    return jsonify(correct=str(correct), tot=str(total))

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

    dot = compute_dot(vector, encrypted_weights)

    return jsonify(serializeArr(dot, 30))


@app.route("/hyperplane_handler", methods=['GET', 'POST'])
def hyperplane_handler():
    input_vec = request.json["vector"]
    response = requests.post("http://127.0.0.1:8000/hyperplane_dot", json={
        "vector": input_vec
    })
    vals, l = deserialize_arr(response.json())
    requests.post("http://127.0.0.1:8000/veu11/init")
    getans = requests.post(
        "http://127.0.0.1:5000/argmax/vector_nokey",
        json={
            "inp": serializeArr(vals, 30)
        }
    )

    return getans.json()


if __name__ == '__main__':
    app.run(debug=True, port=int(sys.argv[1]))
