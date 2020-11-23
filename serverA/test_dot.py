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
	# print(unenc_dotp[", orig)
	# assert dot_p == orig
	# for j in range(15):
	# 	response = requests.post("http://127.0.0.1:5000/veu11_compare_no_priv")
	# 	out = response.json()["t_dec"]
	# 	if a <= b and out == 0:
	# 		print("Test Failed")
	# 	elif a > b and out == 1:
	# 		print("Test Failed")



# client ke paas vector hai  , lekin key nhi hai
# client call krega set_veu11_operands , 
# client cal krega no