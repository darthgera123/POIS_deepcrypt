import flask
from flask import request, jsonify
import random 
app = flask.Flask(__name__)
app.config["DEBUG"] = True
"""
This hosts the model. The client server makes api calls by sending data to the model server
The model server here then responds to those POST requests
"""

@app.route('/api/model/addition',methods = ['GET',"POST"])
def api_addition():
	encrypt_key = random.randint(0,1e5)
	if request.method == 'GET':
		return jsonify(encrypt_key)
	if request.method == 'POST':
		number = request.json['number']
		new_number = int(number) + encrypt_key
		return jsonify(new_number)

@app.route('/api/model/subtraction',methods = ["POST"])
def api_subtraction():
	encrypt_key = random.randint(0,1e5)
	if request.method == 'POST':
		number = request.json['number']
		new_number = int(number) - encrypt_key
		return jsonify(new_number)

if __name__ == '__main__':
	# port 5000
	app.run()