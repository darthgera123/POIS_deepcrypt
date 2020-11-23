import random
import requests
from tqdm import tqdm
from paillierlib import paillier
import numpy as np
# import gmpy2
import json
import math


def serializeArr(gg, l):
    s1 = str(gg[0].c)
    s2 = str(gg[0].n)
    for i in range(1, len(gg)):
        s1 = s1 + ";" + str(gg[i].c)
        s2 = s2 + ";" + str(gg[i].n)
    dic = {"a1": s1, "a2": s2, "a3": l}
    return dic

    # return int(getans.json()['ans']["answer"])


def bayes_enc():

    requests.post("http://127.0.0.1:8000/veu11/init")

    l = 85
    conditional_prob_list = np.load("./COP_ENC.npy", allow_pickle=True)

    class_prior_list = np.load("./CLP_ENC.npy", allow_pickle=True)
    sx, sy, sz = conditional_prob_list.shape
    dict_send = {
        "clp": serializeArr(
            class_prior_list.flatten(),
            l),
        "cop": serializeArr(
            conditional_prob_list.flatten(),
            l),
        "sx": str(sx),
        "sy": str(sy),
        "sz": str(sz)}

    ret = requests.post("http://127.0.0.1:5001/bayes_handler", json=dict_send)

    corr = int(ret.json()['correct'])
    total = int(ret.json()['tot'])
    accuracy = (corr / total) * 100
    print("ENCRYPTED ACCURACY IS ", accuracy)


def computeClassProbs(inp_vec, class_prior_list, conditional_prob_list, flag):
    class_posterior_list = []
    for class_index in range(conditional_prob_list.shape[0]):
        class_prob = class_prior_list[class_index]
        probabilities = conditional_prob_list[class_index][np.arange(
            conditional_prob_list.shape[1]), inp_vec]
        class_prob = class_prob + np.sum(probabilities)
        class_posterior_list.append(class_prob)
    return np.array(class_posterior_list)


def bayes_unenc():

    cop_plain = np.load("./COP_PLAIN.npy")
    clp_plain = np.load("./CLP_PLAIN.npy")
    DATA = np.load("./DATA.npy")
    LABEL = np.load("./LABEL.npy")

    total = DATA.shape[0]
    corr_normal = 0
    for i in tqdm(range(total)):
        inp_vec = DATA[i]

        class_posterior_list_unenc = computeClassProbs(
            inp_vec, clp_plain, cop_plain, True)

        gg = np.argmax(class_posterior_list_unenc)

        if gg == LABEL[i]:
            corr_normal += 1

    print("UNENCRYPTED ACCURACY IS ", 100 * (corr_normal / total))


bayes_unenc()
bayes_enc()
