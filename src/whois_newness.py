"""
 - script_name : whois_newness.py

 - Team members : Eloise, Minjeong, Byungkwon, Taeksang
 - python3 whois_newness.py --inputfile /data/examples/dns10000.log
"""

import argparse
import whois
import time
import socket
from os import path
import json
from dataprun import GenerateWL, GenerateDomain2IP
import numpy as np
from label import Label
import datetime

def whoisLookup_CreationDate(domainName2IndexDictionary, verbose=False):
    domainNameIndex2CreationDateDictionary = {}

    # stores new lookup results not in cache
    newCacheData = {}
    failCacheData = {}

    # records total number of lookups.
    count_totalLookups = 0
    count_unknownTLD = 0
    count_FailedLookups = 0
    count_cacheLookups = 0

    #the whois package only support these Top Level Domains (TLD)
    known_tld = ['ac_uk', 'am', 'amsterdam', 'ar', 'at', 'au', 'bank', 'be', 'biz', 'br', 'by', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'co_il', 'co_jp', 'com', 'com_au', 'com_tr', 'cr', 'cz', 'de', 'download', 'edu', 'education', 'eu', 'fi', 'fm', 'fr', 'frl', 'game', 'global_', 'hk', 'id_', 'ie', 'im', 'in_', 'info', 'ink', 'io', 'ir', 'is_', 'it', 'jp', 'kr', 'kz', 'link', 'lt', 'lv', 'me', 'mobi', 'mu', 'mx', 'name', 'net', 'ninja', 'nl', 'nu', 'nyc', 'nz', 'online', 'org', 'pe', 'pharmacy', 'pl', 'press', 'pro', 'pt', 'pub', 'pw', 'rest', 'ru', 'ru_rf', 'rw', 'sale', 'se', 'security', 'sh', 'site', 'space', 'store', 'tech', 'tel', 'theatre', 'tickets', 'trade', 'tv', 'ua', 'uk', 'us', 'uz', 'video', 'website', 'wiki', 'work', 'xyz', 'za'] #02/23/2022

    # To save time, cache domains that continuously fail to query whois
    if path.exists('domainWhoisQueryFailCache.json'):
        with open("domainWhoisQueryFailCache.json", "r") as cacheFile2Read:
            failCacheData = json.load(cacheFile2Read)
            cacheFile2Read.close()

    # If cache file exist, first lookup in cache
    if path.exists('domainCreationDateCache.json'):
        with open("domainCreationDateCache.json", "r") as cacheFile2Read:
            cacheData = json.load(cacheFile2Read)
        for domainName,domainIndex in domainName2IndexDictionary.items():
            if domainName in cacheData.keys():
                count_cacheLookups = count_cacheLookups+1
                domainNameIndex2CreationDateDictionary[domainIndex] = cacheData[domainName]
            elif domainName.split(".")[-1] not in known_tld:
                # Unknown TLD
                if (verbose):
                    print("[-] UnknownTld : {}".format(domainName))
                count_unknownTLD = count_unknownTLD + 1
            elif domainName in failCacheData.keys():
                # if the domain is in fail cache, just skip to query
                count_FailedLookups = count_FailedLookups+1
                count_cacheLookups = count_cacheLookups+1
                if (verbose):
                    print("[-] Keep failing domain. Skip : {}".format(domainName))
            else:
                # error handling to catch exceptions and connection reset errors with 'whois' lookups
                try:
                    if (verbose):
                        print(domainName)
                    lookupResult = whois.query(domainName)
                    if lookupResult:
                        # retreive timestamp of the created date from whois lookup result
                        creation_date = lookupResult.creation_date
                        if (creation_date is None):
                            raise whois.exceptions.UnknownDateFormat
                        creation_ts = creation_date.timestamp()
                    
                        # result added to dictionary
                        domainNameIndex2CreationDateDictionary[domainIndex] = creation_ts
                        # result added to new cache data
                        newCacheData[domainName] = creation_ts
                    else:
                        count_FailedLookups = count_FailedLookups+1
                        failCacheData[domainName] = "Null Lookup result"
                except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                    count_FailedLookups = count_FailedLookups+1
                    failCacheData[domainName] = "{}".format(e)
                    if (verbose):
                        print(e)
                count_totalLookups = count_totalLookups+1
        # writing new cache data to file appending to older cache data.
        cacheData.update(newCacheData)
        with open("domainCreationDateCache.json", "w") as cachefile:
            json.dump(cacheData, cachefile)
            cachefile.close()
        with open("domainWhoisQueryFailCache.json", "w") as cachefile:
            json.dump(failCacheData, cachefile)
            cachefile.close()

    # If cache file does not exist
    else:
        for domainName,domainIndex in domainName2IndexDictionary.items():
            if domainName in failCacheData.keys():
                # if the domain is in fail cache, just skip to query
                count_cacheLookups = count_cacheLookups+1
                count_FailedLookups = count_FailedLookups+1
                if (verbose):
                    print("[-] Keep failing domain. Skip : {}".format(domainName))
                pass
            elif domainName.split(".")[-1] not in known_tld:
                # Unknown TLD
                if (verbose):
                    print("[-] UnknownTld : {}".format(domainName))
                count_unknownTLD = count_unknownTLD + 1
            else:
                try:
                    if (verbose):
                        print(domainName) # to be deleted
                    lookupResult = whois.query(domainName)
                    if lookupResult:
                        # retreive timestamp of the created date from whois lookup result
                        creation_date = lookupResult.creation_date
                        if (creation_date is None):
                            raise whois.exceptions.UnknownDateFormat
                        creation_ts = creation_date.timestamp()
                        # result added to dictionary
                        domainNameIndex2CreationDateDictionary[domainIndex] = creation_ts 
                        # result added to cache data
                        newCacheData[domainName] = creation_ts
                    else:
                        count_FailedLookups = count_FailedLookups+1
                        failCacheData[domainName] = "Null Lookup result"
                except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                    count_FailedLookups = count_FailedLookups+1
                    failCacheData[domainName] = "{}".format(e)

                count_totalLookups = count_totalLookups+1
        # writing cache data to file
        with open("domainCreationDateCache.json", "w") as cachefile:
            json.dump(newCacheData, cachefile)
            cachefile.close()
        with open("domainWhoisQueryFailCache.json", "w") as cachefile:
            json.dump(failCacheData, cachefile)
            cachefile.close()

    print(f"\nWhois lookups completed. The number of whois query : {count_totalLookups}, the number of cached lookup : {count_cacheLookups}")

    return domainNameIndex2CreationDateDictionary, count_FailedLookups, count_unknownTLD

def potential_threat_newness_criteria0(creation_date):
    # returns the score of potential threat on the creation date
    
    if (creation_date >= 1640995200):
        # when it is newer than 1/1/2022, the potential possibility of being malicious is 30% more.
        return 0.3
    if (creation_date >= 1609459200):
        # when it is newer than 1/1/2021, the potential possibility of being malicious is 15% more.
        return 0.15
    # otherwise 0%
    return 0

def potential_threat_newness_criteria1(creation_date):
    # returns the score of potential threat on the creation date
    
    if (creation_date >= datetime.datetime(2021, 1, 1, 0, 0).timestamp()):
        # when it is newer than 1/1/2021, the potential possibility of being malicious is 15% more.
        #print(creation_date)
        return 0.3
    if (creation_date >= datetime.datetime(2020, 1, 1, 0, 0).timestamp()):
        # when it is newer than 1/1/2020, the potential possibility of being malicious is 30% more.
        #print(creation_date)
        return 0.15
    # otherwise 0%
    return 0

def get_domain_newness(domains: dict, criteria=potential_threat_newness_criteria1) -> np.ndarray:

    #    labeled[index, 0] = 0 # 1 when domain is bad,  0 when good
    #    labeled[index, 1] = 1 # 1 when domain is good, 0 when bad

    #    newness[index, 0] = score # score is determined according to its newness due to its potential danger
    #    newness[index, 1] = 0     # the newness cannot affect the probability of goodness
    creation_date, _ , _ = whoisLookup_CreationDate(domains)

    labeled_addition = np.zeros((len(domains), 2))
    for domain, index in domains.items():
        if index in creation_date:
            labeled_addition[index, 0] = criteria(creation_date[index])
            labeled_addition[index, 1] = 0
            #print("   {}, {}, {}".format(index, creation_date[index], domain))
        else:
            #print("{}, {}".format(index, domain))
            pass

    return labeled_addition

def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, nargs='+', required=True,
                        help="input DNS Source files")

    FLAGS = parser.parse_args()

    # Names of DNS log files stored as filename
    filename = []
    filename = FLAGS.inputfile


    # Calling dataprun package for whitelisted domain names and corresponding indexes
    print("Calling Dataprun package for whitelisted domain names......\n")
    RL,DD,IPD = GenerateWL(filename)

    
    with open("temp_output_domainIndex.txt", "w") as f:
        for i in DD:
            f.write("{} : {}\r\n".format(DD[i], i))
        f.close()
    
    result,fail_count,unknown_count = whoisLookup_CreationDate(DD)
    with open("temp_output_whois_creation.txt", "w") as f:
        for i in result:
            f.write("{} : {}\r\n".format(i,result[i]))
        f.close()
    
    newness = get_domain_newness(DD, criteria=potential_threat_newness_criteria1)
    with open("temp_output_newness_potential_threat.txt", "w") as f:
        for i in range(len(newness)):
            f.write("{} : {} {}\r\n".format(i,newness[i,0],newness[i,1]))
        f.close()

    # creation_date result print
    create_ts = np.array(list(result.items()))[:,1]
    print(np.min(create_ts))
    print(np.max(create_ts))

    #printing the matrix
    print(newness)
    print("newness.shape : {}".format(newness.shape))
    print("\n")

    print(np.unique(newness[:,0], return_counts=True))

    #print(len(result))
    #label = Label()
    #labels = label.get_domain_labels(DD)
    #print("labels.shape : {}".format(labels.shape)) # (1255,2)
    
    print("Total domain number from input: {}".format(len(DD)))
    print("   Number of successful whois query : {}".format(len(result)))
    print("   failed query : {}".format(fail_count))
    print("   Unknown TLD  : {}".format(unknown_count))

if __name__=="__main__":
    main()

