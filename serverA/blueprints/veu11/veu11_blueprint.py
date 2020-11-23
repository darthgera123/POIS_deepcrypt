from flask import Blueprint, Response, Flask, jsonify, render_template, request, url_for, redirect, flash, current_app
from POIS_deepcrypt.dgk import *
from POIS_deepcrypt.serverA.utils import *
import requests
veu11_blueprint = Blueprint('veu11', __name__)


@veu11_blueprint.route('/init', methods=['GET', 'POST'])
def veu11_init():
    global config
    key_pair = np.load("./PAILLIER_KEY.npy", allow_pickle=True)[0]
    gm_key_pair = np.load("./GM_KEY.npy", allow_pickle=True)[0]

    current_app.config["paillier_priv"] = key_pair.private_key
    current_app.config["paillier_pub"] = key_pair.public_key
    current_app.config["gm_priv"] = gm_key_pair["priv"]
    current_app.config["gm_pub"] = gm_key_pair["pub"]

    public_key = {
        "n": int(
            key_pair.public_key.n), "g": int(
            key_pair.public_key.g)}

    response = requests.post("http://127.0.0.1:5000/veu11/set_pub", json={
        'paillier_pub': public_key,
        'gm_pub': current_app.config["gm_pub"],
    })
    if response.status_code != 200:
        print("Public Key sharing failed")

    return Response("", status=200)


@veu11_blueprint.route('/set_pub', methods=['POST'])
def veu11_set_pub():
    global config
    public_key = request.json["paillier_pub"]

    current_app.config['paillier_pub'] = paillier.PaillierPublicKey(
        n=mpz(public_key["n"]), g=int(public_key["g"]))
    current_app.config['gm_pub'] = request.json['gm_pub']
    current_app.config['paillier_priv'] = None
    current_app.config['gm_priv'] = None

    return Response("", status=200)


@veu11_blueprint.route("/compare_no_priv", methods=['GET', 'POST'])
def veu11_compare_no_priv():

    global config, data

    if not current_app.config['paillier_pub'] or current_app.config['paillier_priv']:
        print("Key inconsistency for Veu11.")
        return Response("", status=404)

    if not current_app.config['gm_pub'] or current_app.config['gm_priv']:
        print("Key inconsistency for Goldwasser Micali.")
        return Response("", status=404)

    if not current_app.config["data"]['veu11_operand1'] or not current_app.config["data"]["veu11_operand2"]:
        print("Comparison operands not set for Veu11.")
        return Response("", status=404)

    encrypted_a = current_app.config["data"]["veu11_operand1"]
    encrypted_b = current_app.config["data"]["veu11_operand2"]
    l = current_app.config['dgk_l']

    x = encrypted_b + \
        paillier.encrypt(mpz(pow(2, l)), current_app.config["paillier_pub"]) - encrypted_a
    r = random.getrandbits(l + 2)
    z = x + paillier.encrypt(mpz(r), current_app.config["paillier_pub"])
    c = r % pow(2, l)

    encrypted_z = {
        "c": int(z.c),
        "n": int(z.n),
    }

    dgk_init_without_route(False)
    set_compare_operand_without_route(c)

    response = requests.post(
        "http://127.0.0.1:8000/veu11/compare_has_priv",
        json={
            "z": encrypted_z,
        })

    z_l = response.json()["z_l"]

    t = dgk_compare_has_priv_without_route()

    if MSB(r, l):
        r_l = gm.encrypt(1, current_app.config["gm_pub"])
    else:
        r_l = gm.encrypt(0, current_app.config["gm_pub"])

    N, _ = current_app.config["gm_pub"]
    t_ = (z_l[0] % N * r_l[0] % N) % N
    t = (t_ % N * t % N) % N

    response = requests.post("http://127.0.0.1:8000/print_t", json={"t": t})
    return jsonify(t=t, t_dec=response.json()["t_dec"])

def veu11_compare_no_priv_without_route():

    global config, data

    if not current_app.config['paillier_pub'] or current_app.config['paillier_priv']:
        print("Key inconsistency for Veu11.")
        return Response("", status=404)

    if not current_app.config['gm_pub'] or current_app.config['gm_priv']:
        print("Key inconsistency for Goldwasser Micali.")
        return Response("", status=404)

    if not current_app.config["data"]['veu11_operand1'] or not current_app.config["data"]["veu11_operand2"]:
        print("Comparison operands not set for Veu11.")
        return Response("", status=404)

    encrypted_a = current_app.config["data"]["veu11_operand1"]
    encrypted_b = current_app.config["data"]["veu11_operand2"]
    l = current_app.config['dgk_l']

    x = encrypted_b + \
        paillier.encrypt(mpz(pow(2, l)), current_app.config["paillier_pub"]) - encrypted_a
    r = random.getrandbits(l + 2)
    z = x + paillier.encrypt(mpz(r), current_app.config["paillier_pub"])
    c = r % pow(2, l)

    encrypted_z = {
        "c": int(z.c),
        "n": int(z.n),
    }

    dgk_init_without_route(False)
    set_compare_operand_without_route(c)

    response = requests.post(
        "http://127.0.0.1:8000/veu11/compare_has_priv",
        json={
            "z": encrypted_z,
        })

    z_l = response.json()["z_l"]

    t = dgk_compare_has_priv_without_route()

    if MSB(r, l):
        r_l = gm.encrypt(1, current_app.config["gm_pub"])
    else:
        r_l = gm.encrypt(0, current_app.config["gm_pub"])

    N, _ = current_app.config["gm_pub"]
    t_ = (z_l[0] % N * r_l[0] % N) % N
    t = (t_ % N * t % N) % N

    response = requests.post("http://127.0.0.1:8000/print_t", json={"t": t})
    return t

@veu11_blueprint.route("/compare_has_priv", methods=['GET', 'POST'])
def veu11_compare_has_priv():
    if not current_app.config['paillier_priv']:
        print("Key inconsistency for Veu11.")
        return Response("", status=404)

    if not current_app.config['gm_priv']:
        print("Key inconsistency for Goldwasser Micali.")
        return Response("", status=404)

    z = paillier.PaillierCiphertext(
        c=mpz(
            request.json["z"]["c"]), n=mpz(
            request.json["z"]["n"]))

    z_dec = paillier.decrypt(z, current_app.config["paillier_priv"])
    d = z_dec % pow(2, current_app.config["dgk_l"])

    set_compare_operand_without_route(d)

    if MSB(z_dec, current_app.config["dgk_l"]):
        z_l = gm.encrypt(1, current_app.config["gm_pub"])
    else:
        z_l = gm.encrypt(0, current_app.config["gm_pub"])

    return jsonify(z_l=z_l)
