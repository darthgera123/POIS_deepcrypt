import random	
import requests
from tqdm import tqdm

requests.post("http://127.0.0.1:8000/veu11_init")

for i in tqdm(range(20)):
	a = random.randint(0, pow(2, 20) - 1)
	b = random.randint(0, pow(2, 20) - 1)
	requests.post("http://127.0.0.1:5000/set_veu11_operands", json={"val1":a, "val2":b})
	for j in range(15):
		response = requests.post("http://127.0.0.1:5000/veu11_compare_no_priv")
		out = response.json()["t_dec"]
		if a <= b and out == 0:
			print("Test Failed")
		elif a > b and out == 1:
			print("Test Failed")
