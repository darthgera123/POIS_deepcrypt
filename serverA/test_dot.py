import random	
import requests
from tqdm import tqdm
import numpy as np
requests.post("http://127.0.0.1:8000/veu11/init")

for i in tqdm(range(10)):	
	X = random.sample(range(1,100),1)
	Y = random.sample(range(1,100),1)
	orig = np.dot(X,Y)
	
	reponse =requests.post("http://127.0.0.1:5000/set_dot_product", json={"val2":X})
	response = requests.post("http://127.0.0.1:5000/compute_dot", json={"val1":Y})
	dot_p = response.json()

	c = dot_p["fval"]["paillier_c"]
	n = dot_p["fval"]["paillier_n"]

	response = requests.post("http://127.0.0.1:8000/dot_unenc" , json = {"val1":c, "val2":n})
	print(response.json())
	print(orig)
	assert orig == response.json()['unenc']
