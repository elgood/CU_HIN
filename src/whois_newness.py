"""
 - script_name : whois_newness.py

 - Team members : Eloise, Minjeong, Byungkwon, Taeksang
"""

import argparse
import whois
import time
import socket
from os import path
import json

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
                    lookupResult = whois.query(domainName)
                    if lookupResult:
                        # retreive timestamp of the created date from whois lookup result
                        creation_date = lookupResult.creation_date.timestamp()
                    
                        # result added to dictionary
                        domainNameIndex2CreationDateDictionary[domainIndex] = creation_date
                        # result added to new cache data
                        newCacheData[domainName] = creation_date
                    else:
                        count_FailedLookups = count_FailedLookups+1
                except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                    count_FailedLookups = count_FailedLookups+1
            count_totalLookups = count_totalLookups+1
        # writing new cache data to file appending to older cache data.
        cacheData.update(newCacheData)
        with open("domainCreationDateCache.json", "w") as cachefile:
            json.dump(cacheData, cachefile)

    # If cache file does not exist
    else:
        for domainName,domainIndex in domainName2IndexDictionary.items():
            try:
                lookupResult = whois.query(domainName)
                if lookupResult:
                    # retreive timestamp of the created date from whois lookup result
                    creation_date = lookupResult.creation_date.timestamp()
                    # result added to dictionary
                    domainNameIndex2CreationDateDictionary[domainIndex] = creation_date 
                    # result added to cache data
                    newCacheData[domainName] = creation_date
                else:
                    count_FailedLookups = count_FailedLookups+1
            except (whois.exceptions.FailedParsingWhoisOutput, whois.exceptions.WhoisCommandFailed, whois.exceptions.UnknownDateFormat, socket.error, ConnectionResetError, OSError, KeyError) as e:
                count_FailedLookups = count_FailedLookups+1
            count_totalLookups = count_totalLookups+1
        # writing cache data to file
        with open("domainCreationDateCache.json", "w") as cachefile:
            json.dump(newData, cachefile)

    print(f"\nWhois lookups completed. Total number of lookups : {count_totalLookups}")

    return domainNameIndex2CreationDateDictionary, count_FailedLookups

