import sys
import socket
import tldextract
from difflib import SequenceMatcher
from statistics import mean
import math
import pickle


# this method takes in 2 strings, and returns a float from 0 to 1 indicting
# how similar the strings are.
def stringSimilar(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()


# this method takes 2 domains, extracts their subdomain and domain information,
# and uses string similarity to determine how similar the domains are.
def similarByName(d1, d2):
    # tld.extract(domain) seperates an input domain string into its subdomain,
    # domain, and suffix as a tuple.
    d1_split = tldextract.extract(d1)
    d2_split = tldextract.extract(d2)

    # This does a string similarity call on the domain parts of the domains.
    domain_similarity = stringSimilar(d1_split[1], d2_split[1])
    # This does a string similarity call on the subdomain parts of the domains.
    subdomain_similarity = stringSimilar(d1_split[0], d2_split[0])

    # The average is take becaue we want mail.foo.com and mail.bar.com to have
    # the same similarity value as mail.foo.com and docs.foo.com. Essentially,
    # if the domains match and the subdomains don't, its on par if the
    # subdomains match and the domains don't.
    return(mean([domain_similarity, subdomain_similarity]))


# This takes two ip sub-numbers, and determines how close they are to each
# other
def subIPSimilar(sub1, sub2):
    diff = math.abs(sub1-sub2)
    return math.abs((diff/255)-1)


# This method takes two domain's IP addresses, and determines if they are in
# the same major subnet. If they are, it calculates how close they are based
# on their other IP numbers
def similarByNetwork(d1_ip, d2_ip):
    with open("nomatch.p", "rb") as fp:

        # This is a dictionary of class B networks with no ownership. If a
        # class B network is unowned, we can only use information based on the
        # domain's class A information. See DataProcessing.py for how this
        # dictionary was created
        no_match_dict = pickle.load(fp)

        # This splits each ip address into its 4 subnumbers
        d1split = d1_ip.split(".")
        d2split = d2_ip.split(".")

        # This checks to see if the first number is the same for both IPs.
        # This has to be true, as 2 IPs in the same subnet will always have
        # the same first number
        if d1split[0] == d2split[0]:

            # All the first values of 0-127 are class A networks, and all
            # class A networks are owned. So we only need to do further
            # subnet analysis if their first number is greater than 127
            if int(d1split[0]) > 127:

                # This checks to see if the second number is the same for both
                # IP addresses
                if d1split[1] == d2split[1]:

                    # This checks to see if the class B network found is owned
                    # or not, using the data processing done previously.
                    # If it is unowned, we calculate it as if it were in a
                    # matching class A subnet
                    if d1split[1] in no_match_dict[int(d1split[0])]:

                        # Eventually, these values will be combined into a
                        # single value to be returned
                        sub2 = subIPSimilar(int(d1split[1]), int(d2split[1]))
                        sub3 = subIPSimilar(int(d1split[2]), int(d2split[2]))
                        sub4 = subIPSimilar(int(d1split[3]), int(d2split[3]))

                    # This is the case where the subnet in question is owned,
                    # and numerical analysis can be done just on the last 2
                    # numbers of both IP addresses
                    else:

                        # Eventually, these values will be combined into a
                        # single value to be returned
                        sub3 = subIPSimilar(int(d1split[2]), int(d2split[2]))
                        sub4 = subIPSimilar(int(d1split[3]), int(d2split[3]))

                # This is the case where the first number of both IPs are the
                # same, it is a class B network, and the second number is not
                # the same for both IPs. Thus, they are not in the same
                # class B subnet
                else:
                    return 0

            # This is the case where the first number of both IPs are the same
            # and less than 128. Since all the class A networks are owned,
            # we can jump right to numerical analysis
            else:
                
                # Eventually, these values will be combined into a
                # single value to be returned
                sub2 = subIPSimilar(int(d1split[1]), int(d2split[1]))
                sub3 = subIPSimilar(int(d1split[2]), int(d2split[2]))
                sub4 = subIPSimilar(int(d1split[3]), int(d2split[3]))

        # This is the case where the first number of both IPs don't match
        else:
            return 0


def main():
    domain1 = sys.argv[1]
    domain2 = sys.argv[2]

    try:
        d1_ip = socket.gethostbyname(domain1)
        d2_ip = socket.gethostbyname(domain2)

        text_similar = similarByName(domain1, domain2)
        net_similar = similarByNetwork(d1_ip, d2_ip)

        string = (f"Text similarity: {text_similar}\n"
                  f"Network similarity: {net_similar}\n")
        print(string)
    except socket.gaierror:
        print("One of the input domains cannot be found")


if __name__ == '__main__':
    main()
