import socket
import tldextract
from difflib import SequenceMatcher
from statistics import mean
import pickle
import numpy as np
from scipy.sparse import csr_matrix


def stringSimilar(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()


def similarByName(d1, d2):
    d1_split = tldextract.extract(d1)
    d2_split = tldextract.extract(d2)

    domain_similarity = stringSimilar(d1_split[1], d2_split[1])
    subdomain_similarity = stringSimilar(d1_split[0], d2_split[0])

    return(domain_similarity*0.65 + subdomain_similarity*0.35)


def subIPSimilar(sub1, sub2):
    diff = abs(sub1-sub2)
    return abs((diff/255)-1)


def networkHelper(start, d1split, d2split):
    constants = [0.5, 0.3, 0.15, 0.05]
    sum = 0
    for i in range(start):
        sum += constants[i]
    for i in range(start, 4):
        change = subIPSimilar(int(d1split[i]), int(d2split[i]))
        sum += change * constants[i]
        if change != 1:
            break
    return sum


def similarByNetwork(d1_ip, d2_ip):

    with open("nomatch.p", "rb") as fp:

        d1split = d1_ip.split(".")
        d2split = d2_ip.split(".")

        no_match_dict = pickle.load(fp)

        if d1split[0] != d2split[0]:
            # print("IPs are not similar at all: Not in same subnet.")
            return 0.0
        else:
            if d1split[1] == d2split[1] and d1split[2] == d2split[2] and \
             d1split[3] == d2split[3]:
                return 1.0
            if int(d1split[0]) < 128:
                if int(d1split[0]) in no_match_dict.keys():
                    # print("IPs are not similar: "
                    #       "Simlar Class A subnet is unowned.")
                    return networkHelper(1, d1split, d2split) * 0.8
                else:
                    # print("IPs are in the same Class A subnet.")
                    return networkHelper(1, d1split, d2split)
            else:
                if int(d1split[0]) in no_match_dict.keys() and \
                 int(d1split[1]) in no_match_dict[int(d1split[0])]:
                    # print("IPs are not smilar: "
                    #       "Similar Class B subnet is unowned.")
                    return networkHelper(2, d1split, d2split) * 0.9
                else:
                    # print("IPs are in the same Class B subnet.")
                    return networkHelper(2, d1split, d2split)


def domainSimilarityAlgorithm(domain1, domain2):
    try:
        d1_ip = socket.gethostbyname(domain1)
        d2_ip = socket.gethostbyname(domain2)

        text_similar = similarByName(domain1, domain2)
        net_similar = similarByNetwork(d1_ip, d2_ip)
        total_similar = round(mean([text_similar, net_similar]), 3)

        if total_similar <= 0.2:
            return 0.0
        else:
            return total_similar
    except socket.gaierror:
        return None


def compareDomainsMass(domain_list):
    matrix_size = len(domain_list)
    dense_list = [[0]*matrix_size]*matrix_size

    for i in range(matrix_size):
        for j in range(i, matrix_size):
            similarity = domainSimilarityAlgorithm(domain_list[i],
                                                   domain_list[j],)
            dense_list[j][i] = similarity

    dense_array = np.array(dense_list)

    csr_array = csr_matrix(dense_array)

    return csr_array
