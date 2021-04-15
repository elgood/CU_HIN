"""
- script_name : drd_matrix.py

- For calling the script from another program '(hin.py'),
    step1: from drd_matrix import drdMatrix
    step2: domainRegistrarDomainMatrix = drdMatrix(['filename']) # for multiple files or drdMatrix(filename) for single file

- To run the script as standalone use  command 'python3 drd_matrix.py --inputfile <dns_log_filename> <dns_log_filename> ....
    - (script can take single multiple DNS source log files as input)

- Script will return domain-registrar-domain matrix as CSR sparse matrix
"""

import argparse
import whois
import time
from scipy.sparse import csr_matrix
import dataprun
import socket
from os import path
import json

def csrMatrix(domainNameIndexList, domainNameIndex2RegistrarDictionary):

    """
    - Generates symmetric CSR sparse matrix for two domain names having same registrar.
    - Function takes two arguments: 'domainNameList' which contains list of unique domain
                        names and 'regR' which is a dictionary with domain_names as 
                        keys and registrar of the domain as value.
    - Funcion returns the final CSR sparse matrix.
    - ref:https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html#scipy.sparse.csr_matrix
    """

    # Both rows and columns of the matrix are domain name index from DD dictionary returned from 'dataprun' package 
    rows = domainNameIndexList
    columns = domainNameIndexList
    rowIndex = []
    columnIndex = []
    
    # 'data' is the list containing matrix values which here is 1
    data = []

    # Nested for-loop will compare ith domain-name index in each row with jth domain-name index in each
    # column of the matrix. If both domain-names have same registrar, 'data' at [i][j]th position will
    # be 1. The matrix will be symmetric such that d[i][j]==d[j][i]
    for i in range(len(rows)):
        for j in range(len(columns)):
            if (domainNameIndex2RegistrarDictionary[rows[i]] == domainNameIndex2RegistrarDictionary[columns[j]]):
                data.append(1)
                # Taking the row and column index for when value/data is 1.
                rowIndex.append(i)
                columnIndex.append(j)
    
    # 'rowIndex' and 'columnIndex' are row and column indices where data=1. 'shape' defines shape of the final matrix.
    drdCsrMatrix =  csr_matrix((data, (rowIndex, columnIndex)), shape=(len(rows),len(columns))).toarray()

    return drdCsrMatrix

def whoisLookup(domainName2IndexDictionary):

    """
    - 'whois' python package is used to query for registrar of each domain-names.

    - 'domainName2IndexDictionary' contains  unique domain-names and corresponding
        indexes received from 'dataprune' package.

    - Caches rgistrar lookup response as a json file 'domainRegistrarCache.json' which 
        can be read as a dictionary with domain_name as key and registrar-name as value.

    - 'whois' lookup for registrar is only done if registrar of that domain is not already 
        cached.

    - returns dictionary 'domainNameIndex2RegistrarDictionary' containing domain_name index 
    as key and registrar of the domain-name as value. And 'count_FailedLookups' which is the 
    number of unsuccessful registrar lookups.
    """

    count_FailedLookups = 0
    domainNameIndex2RegistrarDictionary = {}
    
    # stores new lookup results not in cache
    newCacheData = {}
    
    # records total number of lookups.
    count_totalLookups = 0

    # If cache file exist, first lookup in cache
    if path.exists('domainRegistrarCache.json'):
        with open("domainRegistrarCache.json", "r") as cacheFile2Read:
            cacheData = json.load(cacheFile2Read)
        for domainName,domainIndex in domainName2IndexDictionary.items():
            if domainName in cacheData.keys():
                domainNameIndex2RegistrarDictionary[domainIndex] = cacheData[domainName]
            else:
                # error handling to catch exceptions and connection reset errors with 'whois' lookups
                try:
                    lookupResult = whois.query(domainName)
                    if lookupResult:
                        # result added to dictionary
                        domainNameIndex2RegistrarDictionary[domainIndex] = lookupResult.registrar
                        # result added to new cache data
                        newCacheData[domainName] = lookupResult.registrar
                    else:
                        count_FailedLookups = count_FailedLookups+1
                except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                    count_FailedLookups = count_FailedLookups+1
            count_totalLookups = count_totalLookups+1        
        # writing new cache data to file appending to older cache data.    
        cacheData.update(newCacheData)
        with open("domainRegistrarCache.json", "w") as cachefile:
            json.dump(cacheData, cachefile)
    
    # If cache file does not exist
    else:
        for domainName,domainIndex in domainName2IndexDictionary.items():            
            try:
                lookupResult = whois.query(domainName)
                if lookupResult:
                    # result added to dictionary
                    domainNameIndex2RegistrarDictionary[domainIndex] = lookupResult.registrar
                    # result added to cache data
                    newCacheData[domainName] = lookupResult.registrar
                else:
                    count_FailedLookups = count_FailedLookups+1
            except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                count_FailedLookups = count_FailedLookups+1
            count_totalLookups = count_totalLookups+1
        # writing cache data to file    
        with open("domainRegistrarCache.json", "w") as cachefile:
            json.dump(newData, cachefile)

    print(f"\nWhois lookups completed. Total number of lookups : {count_totalLookups}")

    return domainNameIndex2RegistrarDictionary, count_FailedLookups

def drdMatrix(filename):

    """
    - This is the module to be called from 'hin.py'. To do so,
            domainRegistrardomainMatrix = drdMatrix['filename']
            you can pass in a single file or list of files
    
    - returns CSR sparse matrix for two domains having same registrar
    """
    
    #Marking start of run time
    start_time = time.time()

    #the whois package only support these Top Level Domains (TLD)
    known_tld = ['com', 'uk', 'ac_uk', 'ar', 'at', 'pl', 'be', 'biz', 'br', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'jp', 'co_jp', 'cz', 'de', 'store', 'download', 'edu', 'education', 'eu', 'fi', 'fr', 'id', 'in_', 'info', 'io', 'ir', 'is_is', 'it', 'kr', 'kz', 'lt', 'ru', 'lv', 'me', 'mobi', 'mx', 'name', 'net', 'ninja', 'se', 'nu', 'nyc', 'nz', 'online', 'org', 'pharmacy', 'press', 'pw', 'rest', 'ru_rf', 'security', 'sh', 'site', 'space', 'tech', 'tel', 'theatre', 'tickets', 'tv', 'us', 'uz', 'video', 'website', 'wiki', 'xyz']
    
    # Calling dataprun package for whitelisted domain names and corresponding indexes
    print("Calling Dataprun package for whitelisted domain names......\n")
    RL,DD,IPD = dataprun.GenerateWL(filename)
    
    # Filtering the whitelisted domain_names provided by dataprun package
    # with known TLDs supported by the whois package.
    domainName2IndexDictionary = {}
    for domainName,domainIndex in DD.items():
        if domainName.split(".")[-1] in known_tld:
            domainName2IndexDictionary[domainName] = domainIndex
        else:
            pass
    
    # calling 'whoisLookup()' to find registrars for the domain_names.
    print("\nStarting whois lookup for finding registrar of each domain name...\n")
    domainNameIndex2RegistrarDictionary, count_FailedLookups = whoisLookup(domainName2IndexDictionary)

    # getting domain-name indexes of 'domainNameIndex2RegistrarDictionary' to a list.
    domainNameIndexList = []
    for domainNameIndex, registrarName in domainNameIndex2RegistrarDictionary.items():
        domainNameIndexList.append(domainNameIndex)     

    print(f"\nNumber of unseccessful registrar lookups = {count_FailedLookups}\n")
    
    #calling 'csrMatrix()' to generate the domain-registrar-domain matrix
    print("Generating domain_registrar_domain matrix....\n")
    _csrmatrix = csrMatrix(domainNameIndexList,domainNameIndex2RegistrarDictionary)
   
    print("CSR Sparse matrix generation is complete.\n")
    
    #Marking end of run time
    end_time = time.time()
    
    total_time = end_time-start_time
    
    print(f"\nTotal time to run : {total_time} seconds\n")

    return _csrmatrix


def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, nargs='+', required=True,
                        help="input DNS Source files")

    FLAGS = parser.parse_args()

    # Names of DNS log files stored as filename
    filename = []
    filename = FLAGS.inputfile 

    result = drdMatrix(filename)
    
    #printing the matrix
    print(result)
    print("\n")

if __name__=="__main__":
    main()
