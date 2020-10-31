import flask
from flask import request, jsonify, Response
import random 
import dgk as dgk

app = flask.Flask(__name__)
app.config["DEBUG"] = True
config = {}
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
        return jsonify(0)
    else:
        return jsonify(1)
############ DGK #########################


if __name__ == '__main__':
	# port 5000
	app.run()