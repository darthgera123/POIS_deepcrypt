import random
import requests
from tqdm import tqdm
import time


requests.post("http://127.0.0.1:8000/veu11/init")

for i in tqdm(range(1)):
    a = random.randint(pow(2, 68) - 1, pow(2, 70) - 1)
    b = random.randint(pow(2, 68) - 1, pow(2, 70) - 1)
    requests.post(
        "http://127.0.0.1:5000/set_veu11_operands",
        json={
            "val1": a,
            "val2": b})
    for j in range(1):
        T = time.time()
        response = requests.post("http://127.0.0.1:5000/veu11/compare_no_priv")
        print("Veu11 overall: ", time.time() - T)
        out = response.json()["t_dec"]
        if a <= b and out == 0:
            print("Test Failed")
        elif a > b and out == 1:
            print("Test Failed")


# client ke paas vector hai  , lekin key nhi hai
# client call krega set_veu11_operands ,
# client cal krega no
