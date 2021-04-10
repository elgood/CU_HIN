import json
import os.path
import logging
import pydnsbl
import tldextract
import numpy as np

from concurrent.futures import ThreadPoolExecutor

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

"""
Returns label matrix for domains.

If domain is on blacklist --> [1, 0]
If domain is on whitelist --> [0, 1]
If domain is on both blacklist and whitelist --> [1, 0]
If domain is on neither blacklist and whitelist --> [0, 0]

from src.label import Label
labeler = Label()
labeler.get_domain_labels({"google.com": 0, "test.com": 1})
"""
class Label:
    def __init__(self):
        self.cache_filename = os.path.join(__location__, 'label_cache.json')
        self.whitelist_filename = os.path.join(__location__, 'whitelist.json')
        self.blacklist_filename = os.path.join(__location__, 'blacklist.json')

        # Acceptable TLDs
        self.tld_whitelist = ["gov", "mil"]

        with ThreadPoolExecutor() as executor:
            self.whitelist = self.list_lower(executor.submit(self.__load_json_file, self.whitelist_filename).result())
            self.blacklist = self.list_lower(executor.submit(self.__load_json_file, self.blacklist_filename).result())

            # Load cache if it exists, otherwise create it.
            if os.path.exists(self.cache_filename):
                self.cache = executor.submit(self.__load_json_file, self.cache_filename).result()
            else:
                self.cache = {}
                executor.submit(self.__save_label_cache())

    def label(self, domain: str) -> int:
        with ThreadPoolExecutor() as executor:
            isMalicious = executor.submit(self.check_for_malicious_domain, domain).result()
            isBenign = executor.submit(self.check_for_benign_domain, domain).result()
        
        if (isMalicious):
            self.__add_to_label_cache(domain, 'malicious')
            return 1
        if (isBenign):
            self.__add_to_label_cache(domain, 'benign')
            return 0
        return -1

    def check_for_malicious_domain(self, domain: str) -> bool:
        logging.debug("Checking if domain " + domain + " is on blocklist.")
        domainInfo = tldextract.extract(domain)
        root = '{}.{}'.format(domainInfo.domain, domainInfo.suffix).lower()

        if domain in self.blacklist or root in self.blacklist:
            return True

        alternatives = self.get_domain_variations(root)
        if 'www' not in domain:
            alternatives += self.get_domain_variations(domain)

        for url in alternatives:
            if url in self.blacklist:
                return True
            
        domain_checker = pydnsbl.DNSBLDomainChecker()

        try:
          result = domain_checker.check(domain).blacklisted
        except ValueError:
          logging.warn("Error checking domain: " + domain)
          result = False
        return result

    def check_for_benign_domain(self, domain: str) -> bool:
        logging.debug("Checking if domain " + domain + " is on whitelist.")
        domainInfo = tldextract.extract(domain)
        root = '{}.{}'.format(domainInfo.domain, domainInfo.suffix).lower()
        
        if domainInfo.suffix in self.tld_whitelist:
            return True

        if domain in self.whitelist or root in self.whitelist:
            return True

        alternatives = self.get_domain_variations(root)
        if 'www' not in domain:
            alternatives += self.get_domain_variations(domain)

        for url in alternatives:
            if url in self.whitelist:
                return True
        return False

    def get_domain_variations(self, domain: str) -> list:
        prefixes = ["https://www.", "http://www.", "www."]
        return [prefix + domain for prefix in prefixes]

    def list_lower(self, list: list) -> list:
        return [domain.lower() for domain in list]

    """
    Params: Dictionary with domain as key and index as value. Ex. {"google.com": 0}
    Returns: Labels represented as matrix:

            If domain is on blacklist --> [1, 0]
            If domain is on whitelist --> [0, 1]
            If domain is on both blacklist and whitelist --> [1, 0]
            If domain is on neither blacklist and whitelist --> [0, 0]
    """
    def get_domain_labels(self, domains: dict) -> np.ndarray:
        labeled = np.zeros((len(domains), 2))
        for domain, index in domains.items():
            domain = domain.lower()
            cached_label = self.__check_label_cache(domain)
            label = self.label(domain) if (cached_label == None) else cached_label
            if label == -1: # We don't know!
                labeled[index, 0] = 0
                labeled[index, 1] = 0
            elif label == 0: # benign
                labeled[index, 0] = 0
                labeled[index, 1] = 1
            else: # malicious
                labeled[index, 0] = 1
                labeled[index, 1] = 0
        return labeled

    """
    Internal class methods for json cache management

    This is a poor man's cache. It will get large, and there is no logic for cache replacement.
    """
    def __check_label_cache(self, domain):
        logging.debug("Checking if domain " + domain + " is in cache.")
        if domain in self.cache:
            if self.cache[domain].lower() == "malicious":
                return 1
            elif self.cache[domain].lower() == "benign":
                return 0
            return -1

    def __add_to_label_cache(self, domain, label):
        self.cache[domain] = label
        with ThreadPoolExecutor() as executor:
            executor.submit(self.__save_label_cache)

    def __save_label_cache(self):
        with open(self.cache_filename, 'w') as json_file:
            json.dump(self.cache, json_file, indent=4)

    def __load_json_file(self, json_filename):
        with open(json_filename) as json_file:
            return json.load(json_file)