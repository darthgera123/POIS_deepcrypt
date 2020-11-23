import random
import requests
from tqdm import tqdm

requests.post("http://127.0.0.1:8000/veu11/init")

correct_count = 0
total_tests = 20

for i in tqdm(range(total_tests)):
    a = random.randint(pow(2, 68) - 1, pow(2, 70) - 1)
    b = random.randint(pow(2, 68) - 1, pow(2, 70) - 1)
    requests.post(
        "http://127.0.0.1:5000/set_veu11_operands",
        json={
            "val1": a,
            "val2": b})
    
    response = requests.post("http://127.0.0.1:5000/veu11/compare_no_priv")
    out = response.json()["t_dec"]
    if a <= b and out == 0:
        print("Test Failed")
    elif a > b and out == 1:
        print("Test Failed")
    else:
        correct_count += 1

print("Total Tests", total_tests)
print("Tests Passed", correct_count)
