#!/usr/bin/env python3

import argparse
import whois
import time
import numpy as np
import csv

#run domains through a whois query
#exclude results from domains where whois reports None, meaning domain not found
def whoIsQuery(domain):
    data = whois.query(domain)
    if data is not None:
        (expiration, registrar, creation) = data.expiration_date, data.registrar, data.creation_date
        return(expiration, registrar, creation)

#open the file in read only. Search through file for 'A' or 'AAAA'
#if either are found, so to the 9th column and pull the domain from there
def getDomainName(filename):
    with open(filename, 'r') as infile:
        domain = infile.readlines()
    domain_name = []

    #skip the first 8 lines since they are comments/headers
    for i in range(8,len(domain)):
        line = domain[i].split()
        try:

            # the 13th column is where the A or the AAAA will occur
            if line[13] == 'A' or line[13] == 'AAAA':

                #the 9th colum is where the domain is locates
                domain_name.append(line[9])  
        except Exception:
          print("Ran into problem on line " + str(i))

    domain_names = set(domain_name)
    return domain_names

def main():
    netflowInput = input('Enter the file name: ')
    domain_names = getDomainName(netflowInput)


    #write the domains pulled to a new file and split with lines
    #commented out for now just to ensure I won't need it in the future
    #file = open('domain_name.txt', 'w')
    #for domain_name in domain_names:
        #file.write(domain_name + '\n')
    #file.close()
    #return domain_names

    # writing the whois results to a csv file
    #currently only using the expriation date, registrar, and creation data but might add more later
    with open('domain_whois.csv', 'w') as file:
        csv_writer = csv.writer(file, delimiter =',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["expiration_date, registrar, creation_data"])
        for domain_name in domain_names:
            whois_data = whoIsQuery(domain_name)
            if whois_data is not None:
                #print(whois_data)
                csv_writer.writerow([whois_data[0],whois_data[1],whois_data[2]])
            else:
                print(domain_name)

if __name__=="__main__":
    main()

#to test the data, we just created a file with about 30 lines of dns data found in the class server. 
#we used this to ensure that the code is collecting the data expected. 