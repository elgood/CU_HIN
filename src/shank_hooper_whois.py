#!/usr/bin/env python3

import argparse
import whois
import time
import numpy as np
import csv


def whoIsQuery(domain):
    data = whois.query(domain)
    (expiration, registrar, creation) = data.expiration_date, data.registrar, data.creation_date
    return(expiration, registrar, creation)

#open the file in read only. Search through file for 'A' or 'AAAA'
#if either are found, so to the 9th column and pull the domain from there
def getDomainName(filename):
    with open(filename, 'r') as infile:
        domain = infile.readlines()
    domain_name = []
    for i in range(8,len(domain)):
        line = domain[i].split()
        if line[13] == 'A' or line[13] == 'AAAA':
            domain_name.append(line[9])    
        print(i)

    domain_names = set(domain_name)
    return domain_names

def main():
    netflowInput = input('Enter the file name: ')
    domain_names = getDomainName(netflowInput)

    #write the domains pulled to a new file and split with lines
    #file = open('domain_name.txt', 'w')
    #for domain_name in domain_names:
    #    file.write(domain_name + '\n')
    #file.close()
    #return domain_names


    with open('domain_whois.csv', 'w') as file:
        csv_writer = csv.writer(file, delimiter =',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["expiration_date, registrar, creation_data"])
        for domain_name in domain_names:
            whois_data = whoIsQuery(domain_name)
            csv_writer.writerow([whois_data[0],whois_data[1],whois_data[2]])

if __name__=="__main__":
    main()


#from whois take domain registry domain info

