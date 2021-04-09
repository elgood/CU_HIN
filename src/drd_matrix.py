"""
- script_name : drd_matrix.py
- script can be run with command 'python3 drd_matrix.py --inputfile <dns_log_filename> --num <number_of_domain_names>
    '--num' flag is optional, but if not specified, it will use all domain_names found in the file 
    to form the matrix which will be large and takes lot of time.
- script will fetch 'domain names' from the dns query-requests from file and use filter
it aginst the domain name dictionary which contains whitelisted domain names retuend by 
dataprune script. 
- the final domain name list is used with 'whois' python library to find registrar for 
each domain name. And the 'domain_name:registrar' information is stored in a dictionary
which is then used to generate a CSR sparse matrix with the domain names as rows and 
columns. And for the domain_names with same registrar will have a value of 1 in the matrix.
"""

import argparse
import whois
import time
from scipy.sparse import csr_matrix
import dataprun
import socket

def csrMatrix(domainNameList, regR):

    """
    - The function calculates CSR sparse matrix for the domain-registrar-domain matrix.
    - Function takes two arguments: 'domainNameList' which contains list of unique domain
                        names and 'regR' which is a dictionary with domain_names as 
                        keys and registrar of the domain as value.
    - Funcion returns the final CSR sparse matrix.
    - ref:https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html#scipy.sparse.csr_matrix
    """

    #Both rows and columns of the matrix are domain names
    rows = domainNameList
    columns = domainNameList
    rws = []
    cols = []
    data = []
    #For loop to compare each domain_name in the row with each domain_name in the
    #column to see if they have the same registrar. And if so, value at that [i][j]th
    #position will be 1. The matrix will be symmetric such that d[i][j]==d[j][i]
    for i in range(len(rows)):
        for j in range(len(columns)):
            if (regR[rows[i]] == regR[columns[j]]):
                data.append(1)
                #Taking row and column index for when value is 1.
                rws.append(i)
                cols.append(j)
    #'data' is the list of positions where value is 1. 'rws' and 'cols' are corresponding 
    #row and column indices. 'shape' defines shape of the final matrix.
    drdCsrMatrix =  csr_matrix((data, (rws, cols)), shape=(len(rows),len(columns))).toarray()
    return drdCsrMatrix

def getDomainName(filename):

    """
    - Function to fetch domain names from input file and store them in a list.
    - Function returns the list 'domain_name'
    """

    # Reading lines from input file
    with open(filename, 'r') as infile:
        domain = infile.readlines()
        infile.close()
        domain_name = []
        limit = len(domain)-8

        # From each line, storing domain_name from 10th column to to list
        for i in range(8, limit):
            domain_name.append(domain[i].split('\t')[9])
        #Making the domain names in the list unique
        domain_name = set(domain_name)
    return domain_name

def whoisLookup(dnameList, num):

    """
    - Function uses 'whois' python package to query for registrar of each domain_names.
    - Function takes one argument : 'dnameList' which is the list of unique domain names
    after pruning with the whitelisted domain_names from dataprune.py script.
    - Function returns : 'regR' which is a dictionary with 'domain_name' as key and 
    corresponding 'registrar' as value. And 'count' which is the number of unsuccessful 
    registrar lookups.
    """

    count = 0
    #This part of the code is for the test to limit the number of domain_names queried
    #to first num names. For the unittest #num=20
    domNames = []
    if (num == 0):
        domNames = dnameList
    else:
        for i in range(num):
            domNames.append(dnameList[i])
    regR = {}

    #try-except to catch errors when registar lookups fail due to unknown domain_names or
    #invalid format of data returned.
    cnt = 0
    for i in domNames:
        try:
            lookupResult = whois.query(i)
            if lookupResult:
                regR[i] = lookupResult.registrar
                cnt = cnt+1
            else:
                count = count+1
                cnt = cnt+1
        except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
            count = count+1
            cnt=cnt+1
            time.sleep(3)
            pass
    print(f"\nNumber of lookups : {cnt}")
    return regR, count

def drdMatrix(filename, num, flag):

    """
    - This is the main function in this script. It takes in two arguments: 'filename' which is
    aboslute path for the dns log file which is taken as cmd input with '--inputfile' cmd. And 
    'flag' which is used for unittesting, default flag is 'False', but when called from unittest
    script, flag becomes 'True' so that script is run on limited number of domain_names.
    - This function calls other subfunctions: 'getDomainName()' which gathers domain name from
    the input DNS log file, 'whoisLookup()' which does whois query for each domain_name to find 
    it's registrar, and 'csrMatrix()' which generates a CSR sparse matrix with the domain_names 
    which have same registrars.
    """

    #the whois package only support these TLD
    known_tld = ['com', 'uk', 'ac_uk', 'ar', 'at', 'pl', 'be', 'biz', 'br', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'jp', 'co_jp', 'cz', 'de', 'store', 'download', 'edu', 'education', 'eu', 'fi', 'fr', 'id', 'in_', 'info', 'io', 'ir', 'is_is', 'it', 'kr', 'kz', 'lt', 'ru', 'lv', 'me', 'mobi', 'mx', 'name', 'net', 'ninja', 'se', 'nu', 'nyc', 'nz', 'online', 'org', 'pharmacy', 'press', 'pw', 'rest', 'ru_rf', 'security', 'sh', 'site', 'space', 'tech', 'tel', 'theatre', 'tickets', 'tv', 'us', 'uz', 'video', 'website', 'wiki', 'xyz']

    #Getting domain names from DNS sourcefile
    domain_name_unfiltered = getDomainName(filename)
    
    #skipping dataprun for unittest run
    if (flag == True):
        # Filtering domain_names provided with known TLDs supported by the whois package.
        filteredDomainList = []
        for dName in domain_name_unfiltered:
            if dName.split(".")[-1] in known_tld:
                filteredDomainList.append(dName)
            else:
                pass
    # Not skippiing dataprun for actual code run
    else:
        # Calling dataprun package for pruning domains
        RL,DD,IPD = dataprun.GenerateWL([filename])
    
        # Filtering the whitelisted domain_names provided by dataprun package
        # with known TLDs supported by the whois package.
        domainList = []
        for k,v in DD.items():
            if k.split(".")[-1] in known_tld:
                domainList.append(k)
            else:
                pass

        # Comparing domain_names read from file with whitelisted domain_names from 
        # dataprun package to select only domain_names that are whitelisted
        filteredDomainList = []
        for name in domain_name_unfiltered:
            if name in domainList:
                filteredDomainList.append(name)
            else:
                pass

        # calling 'whoisLookup()' to find registrars for the domain_names.
        #  function returns a dictionary of 'domain_names:registrar' and count
        # of unsuccessful registrar lookups
    regR, count = whoisLookup(filteredDomainList, num)

    # seperating domain_names and registrar from the dictionary 'regR' in
    # to seperate lists.
    domainNameList = []
    registrarNameList = []
    for key, value in regR.items():
        domainNameList.append(key)     # storing domain_names from the dictionary in to a new list
        registrarNameList.append(value)   # storing reg_names from dictionary into a new list

    print(f"\nNumber of unseccessful registrar lookups = {count}\n")
    
    #calling 'csrMatrix()' to generate the domain-registrar-domain matrix
    _csrmatrix = csrMatrix(domainNameList,regR)
    
    return _csrmatrix


def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="input csv file")
    parser.add_argument('--num', type=int, default=0, required=False,
                        help="Number of domain_names used in the matrix.")
    FLAGS = parser.parse_args()

    ##DNS filename to be read stored as filename
    filename = FLAGS.inputfile 

    #number of domain_names to be used in matrix stored as count
    num = FLAGS.num 
    
    #setting intial value of flag to 'True' to 'not skip' dataprun.
    flag = False
    
    #calculating total time taken to run the script
    start_time = time.time()
    result = drdMatrix(filename, num, flag)
    end_time = time.time()
    total_time = end_time-start_time
    print(f"\nTotal time take : {total_time}\n")
    
    #printing the matrix
    print(result)

if __name__=="__main__":
    main()
