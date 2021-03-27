# Code to parse the DNS file, grab domain names, perfom whois query with the domain names
# to get registrar name and return a dictionary with domain name as key and registrar
# name as value

import argparse
import whois
import time
import numpy as np
from scipy.sparse import csr_matrix
import dataprun

def csrMatrix(domList, regR):

    domList1 = []
    domList2 = []
    for i in range(len(domList)): #Splitting the list of domain names in to two halves bases on odd/even indices
        if (i %2 == 0):
            domList1.append(domList[i])
        else:
            domList2.append(domList[i])
#    docs = [domList1, domList2]
#    indptr = [0]
#    indices = []
#    data = []
#    vocabulary = {}
#    
#    for d in docs:
#        for term in d:
#            index = vocabulary.setdefault(term, len(vocabulary))
#            indices.append(index)
#            data.append(1)
#            indptr.append(len(indices))
#
#    return csr_matrix((data, indices, indptr), dtype=int).toarray()

    data = np.zeros((len(domList1), len(domList2))) #defining shape of the matrix
    for i in range(len(domList1)):
        for j in range(len(domList2)):
            if (regR[domList1[i]] == regR[domList2[j]]): #checking if ith domain_name and jth domain_name has the same registrar
                data[i][j] = 1

    return csr_matrix(data.T).toarray() # returns the matrix

#getting domain names from the input DNS file
def getDomainName(filename, count):
    with open(filename, 'r') as infile:
        domain = infile.readlines()
        infile.close()
        domain_name = []
        
        if count < len(domain): # if inout lines count to be read is less than total number of lines, read input line count, else read total lines.
            limit = 8+count
        else:
            limit = len(count)
        
        for i in range(8, limit):
#        for i in range(8, len(domain)):
#            domain_name.append(domain[i].split('\t')[6])
            domain_name.append(domain[i].split('\t')[9])
        domain_name = set(domain_name)  # set type so that all domain names will be unique
    return domain_name

#doing whois lookup for each of the domain name and printing domain name and registrar
def whoisLookup(dname):
#    count=1
    regR = {}
    for i in dname:
        try:
            domain = whois.query(i)
            if domain:
                regR[i] = domain.registrar
#                print(str(count)+"\t"+i+"\t"+domain.registrar+"\n")
#                time.sleep(10)
            else:
                print("Nothing found for "+i+"\n")
        except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, KeyError) as e:
            pass
#        count=count+1
    if (len(regR) %2 !=0): # making sure that the dictionary will always have even number of key-value pairs so that we will get a nxn matrix
        regR.popitem()
    else:
        pass
    return regR

def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="input csv file")
    parser.add_argument('--n', type=int, required=True,
                        help="Number of lines to read from DNS Source file.")
    FLAGS = parser.parse_args()
    filename = FLAGS.inputfile #DNS filename to be read stored as filename
    count = FLAGS.n #number of lines to be read stored as count

    #the whois package only support these TLD
    known_tld = ['com', 'uk', 'ac_uk', 'ar', 'at', 'pl', 'be', 'biz', 'br', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'jp', 'co_jp', 'cz', 'de', 'store', 'download', 'edu', 'education', 'eu', 'fi', 'fr', 'id', 'in_', 'info', 'io', 'ir', 'is_is', 'it', 'kr', 'kz', 'lt', 'ru', 'lv', 'me', 'mobi', 'mx', 'name', 'net', 'ninja', 'se', 'nu', 'nyc', 'nz', 'online', 'org', 'pharmacy', 'press', 'pw', 'rest', 'ru_rf', 'security', 'sh', 'site', 'space', 'tech', 'tel', 'theatre', 'tickets', 'tv', 'us', 'uz', 'video', 'website', 'wiki', 'xyz']

    #Getting domain names from DNS sourcefile
    domain_name_unfiltered = getDomainName(filename, count)

    #Filtering domain names based on known valid TLD 
    domain_name = []
    for i in domain_name_unfiltered:
        if i.split(".")[-1] in known_tld:
            domain_name.append(i)
        else:
            pass
    
    # Calling dataprun package for pruning domains
    RL,TD = dataprun.GenerateWL([filename])
    DD,CD,IPD = TD
    domList = []
    for name in domain_name:
        if name in DD.values():
            domList.append(name)
        else:
            pass

    regR = whoisLookup(domList)

    domList = []
    regList = []
    for key, value in regR.items():
        domList.append(key)     # storing domain_names from the dictionary in to a new list
        regList.append(value)   # storing reg_names from dictionary into a new list

    _csrmatrix = csrMatrix(domList, regR) #passing list of domain_names and dictioanry to func csrMatrix which will generate a nxn matrix
    print(regR)
    print("\n")
    print(_csrmatrix)

if __name__=="__main__":
    main()
