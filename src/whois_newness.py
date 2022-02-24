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

def whoisLookup_CreationDate(domainName2IndexDictionary):
    count_FailedLookups = 0
    domainNameIndex2CreationDateDictionary = {}

    # stores new lookup results not in cache
    newCacheData = {}

    # records total number of lookups.
    count_totalLookups = 0

    # If cache file exist, first lookup in cache
    if path.exists('domainCreationDateCache.json'):
        with open("domainCreationDateCache.json", "r") as cacheFile2Read:
            cacheData = json.load(cacheFile2Read)
        for domainName,domainIndex in domainName2IndexDictionary.items():
            if domainName in cacheData.keys():
                domainNameIndex2CreationDateDictionary[domainIndex] = cacheData[domainName]
            else:
                # error handling to catch exceptions and connection reset errors with 'whois' lookups
                try:
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
                        # result added to new cache data
                        newCacheData[domainName] = creation_ts
                    else:
                        count_FailedLookups = count_FailedLookups+1
                except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                    count_FailedLookups = count_FailedLookups+1
                    print(e)
            count_totalLookups = count_totalLookups+1
        # writing new cache data to file appending to older cache data.
        cacheData.update(newCacheData)
        with open("domainCreationDateCache.json", "w") as cachefile:
            json.dump(cacheData, cachefile)

    # If cache file does not exist
    else:
        for domainName,domainIndex in domainName2IndexDictionary.items():
            try:
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
            except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                count_FailedLookups = count_FailedLookups+1
            count_totalLookups = count_totalLookups+1
        # writing cache data to file
        with open("domainCreationDateCache.json", "w") as cachefile:
            json.dump(newCacheData, cachefile)

    print(f"\nWhois lookups completed. Total number of lookups : {count_totalLookups}")

    return domainNameIndex2CreationDateDictionary, count_FailedLookups

def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, nargs='+', required=True,
                        help="input DNS Source files")

    FLAGS = parser.parse_args()

    # Names of DNS log files stored as filename
    filename = []
    filename = FLAGS.inputfile

    #the whois package only support these Top Level Domains (TLD)
    #known_tld = ['com', 'uk', 'ac_uk', 'ar', 'at', 'pl', 'be', 'biz', 'br', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'jp', 'co_jp', 'cz', 'de', 'store', 'download', 'edu', 'education', 'eu', 'fi', 'fr', 'id', 'in_', 'info', 'io', 'ir', 'is_is', 'it', 'kr', 'kz', 'lt', 'ru', 'lv', 'me', 'mobi', 'mx', 'name', 'net', 'ninja', 'se', 'nu', 'nyc', 'nz', 'online', 'org', 'pharmacy', 'press', 'pw', 'rest', 'ru_rf', 'security', 'sh', 'site', 'space', 'tech', 'tel', 'theatre', 'tickets', 'tv', 'us', 'uz', 'video', 'website', 'wiki', 'xyz']
    known_tld = ['ac_uk', 'am', 'amsterdam', 'ar', 'at', 'au', 'bank', 'be', 'biz', 'br', 'by', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'co_il', 'co_jp', 'com', 'com_au', 'com_tr', 'cr', 'cz', 'de', 'download', 'edu', 'education', 'eu', 'fi', 'fm', 'fr', 'frl', 'game', 'global_', 'hk', 'id_', 'ie', 'im', 'in_', 'info', 'ink', 'io', 'ir', 'is_', 'it', 'jp', 'kr', 'kz', 'link', 'lt', 'lv', 'me', 'mobi', 'mu', 'mx', 'name', 'net', 'ninja', 'nl', 'nu', 'nyc', 'nz', 'online', 'org', 'pe', 'pharmacy', 'pl', 'press', 'pro', 'pt', 'pub', 'pw', 'rest', 'ru', 'ru_rf', 'rw', 'sale', 'se', 'security', 'sh', 'site', 'space', 'store', 'tech', 'tel', 'theatre', 'tickets', 'trade', 'tv', 'ua', 'uk', 'us', 'uz', 'video', 'website', 'wiki', 'work', 'xyz', 'za'] #02/23/2022

    # Calling dataprun package for whitelisted domain names and corresponding indexes
    print("Calling Dataprun package for whitelisted domain names......\n")
    RL,DD,IPD = GenerateWL(filename)

    # Filtering the whitelisted domain_names provided by dataprun package
    # with known TLDs supported by the whois package.
    domainName2IndexDictionary = {}
    
    unknown_count = 0

    for domainName,domainIndex in DD.items():
        if domainName.split(".")[-1] in known_tld:
            domainName2IndexDictionary[domainName] = domainIndex
        else:
            print("[-] UnknownTld : {}".format(domainName))
            unknown_count = unknown_count + 1
            pass

    with open("temp_output_domainIndex.txt", "w") as f:
        for i in domainName2IndexDictionary:
            f.write("{} : {}\r\n".format(domainName2IndexDictionary[i], i))
        f.close()

    result,fail_count = whoisLookup_CreationDate(domainName2IndexDictionary)
    with open("temp_output_whois_creation.txt", "w") as f:
        for i in result:
            f.write("{} : {}\r\n".format(i,result[i]))
        f.close()

    #printing the matrix
    print(result)
    print("\n")
    
    print("Total domain number from input: {}".format(len(DD)))
    print("Number of successful whois query : {}".format(len(result)))
    print("   failed query : {}".format(fail_count))
    print("   Unknown TLD  : {}".format(unknown_count))

if __name__=="__main__":
    main()

