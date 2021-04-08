import socket
import tldextract
from difflib import SequenceMatcher
from statistics import mean
import pickle
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
import logging


def stringSimilar(s1, s2):
    """Returns the simiarity of two strings. See difflib documentation"""
    return SequenceMatcher(None, s1, s2).ratio()


def similarByName(d1, d2):
    """
    Takes in two domains, and returns the text-based similarity of them

    Parameters:
        d1 (string): the first domain name
        d2 (string): the second domain name

    Returns:
        float: the similarity value
    """
    d1_split = tldextract.extract(d1)
    d2_split = tldextract.extract(d2)

    domain_similarity = stringSimilar(d1_split[1], d2_split[1])
    subdomain_similarity = stringSimilar(d1_split[0], d2_split[0])

    return(domain_similarity*0.65 + subdomain_similarity*0.35)


def subIPSimilar(sub1, sub2):
    """Returns the scaled difference between the CIDR block prefixes"""
    diff = abs(sub1-sub2)
    return abs((diff/255)-1)


def networkHelper(start, d1split, d2split):
    """
    Helper method for network similarity between two IP addresses

    Parameters:
        start (int): the starting CIDR block to analyze from
        d1split (list): split list of first IP address
        d2split (list): split list of second IP address

    Returns:
        float: the similarity value
    """
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
    """
    Determines network similarity between two IP addresses

    Parameters:
        d1_ip (string): the first IP address
        d2_ip (string): the second IP address

    Returns:
        float: the similarity value
    """

    try:
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
    except Exception:
        logging.warn("Problems calculating similarByNetwork for " + d1_ip + 
          " " + d2_ip)
        return 0

def domainSimilarityAlgorithm(domain1: str, domain2: str, 
                              domain2ip: dict) -> float:
                              
    """
    Determines the overall similarity between two domains

    Parameters:
        domain1: str - the first domain
        domain2: str - the second domain
        domain2ip: dict - Mapping from domain to list of ips. 

    Returns:
        float: the similarity value
        None: if either domain didn't resolve
    """
    try:
      d1_ip = domain2ip[domain1][0] # Use the first ip 
      d2_ip = domain2ip[domain2][0] # Use the first ip 
      net_similar = similarByNetwork(d1_ip, d2_ip)
    except KeyError:
      net_similar = None  
    #d1_ip = socket.gethostbyname(domain1)
    #d2_ip = socket.gethostbyname(domain2)

    text_similar = similarByName(domain1, domain2)
   
    if net_similar is None:
      net_similar = text_similar
    
    total_similar = round(mean([text_similar, net_similar]), 3)

    return total_similar
    #except socket.gaierror:
    #    return None


def getDomainSimilarityCSR(domain2index: dict, 
                           domain2ip: dict, 
                           threshold: float):
    """
    Creates a CSR matrix of domain similarities for each combination of domains

    Parameters:
        domain2index: dict - Mapping from domain to integer index.
        domain2ip: dict - Mapping from

    Returns:
        numpy.csr_matrix: the CSR matrix of similarities between the domains
    """
    n = len(domain2index)
    lol = lil_matrix((n,n))

    for d1 in domain2index:
        for d2 in domain2index:
            similarity = domainSimilarityAlgorithm(d1, d2, domain2ip)
            if similarity > threshold:
                i = domain2index[d1]
                j = domain2index[d2]
                lol[i, j] = similarity

    csr_array = lol.tocsr()

    return csr_array
