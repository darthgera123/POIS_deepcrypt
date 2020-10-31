from flask import Response, Flask, jsonify, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename
from forms import DataForm
import requests
import dgk as dgk
import numpy as np

app = Flask(__name__)
app.config["DEBUG"] = True
config = {}
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

############  DGK #########################

#test commands: 
# requests.post("http://127.0.0.1:8000/dgk_init", json={'regen': False})
# c = requests.post("http://127.0.0.1:5000/dgk_encrypt", json={'m': 123}).json()
# m = requests.post("http://127.0.0.1:8000/dgk_decrypt", json={'c': c})




if __name__=='__main__':
	# port 5000 for this and 8000 for server B
    app.run(debug=True,port=8000)
    
