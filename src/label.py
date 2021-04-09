import os
import json
import pydnsbl
import tldextract
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging

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
    # Acceptable TLDs
    whitelist = ["gov", "mil"]

    def label(self, domain: str) -> int:
        with ThreadPoolExecutor() as executor:
            isMalicious = executor.submit(self.check_for_malicious_domain, domain).result()
            isBenign = executor.submit(self.check_for_benign_domain, domain).result()
        
        if (isMalicious):
            return 1
        if (isBenign):
            return 0
        return -1

    def check_for_malicious_domain(self, domain: str) -> bool:
        logging.debug("Checking if domain " + domain + " is on blocklist.")
        domainInfo = tldextract.extract(domain)
        root = '{}.{}'.format(domainInfo.domain, domainInfo.suffix).lower()

        with open(os.path.join(__location__, 'blacklist.json')) as json_file:
            blacklist = json.load(json_file)
            blacklist = self.list_lower(blacklist)

            if domain in blacklist or root in blacklist:
                return True

            alternatives = self.get_domain_variations(root)
            if 'www' not in domain:
                alternatives += self.get_domain_variations(domain)

            for url in alternatives:
                if url in blacklist:
                    return True
            
        domain_checker = pydnsbl.DNSBLDomainChecker()

        try:
          result = domain_checker.check(domain).blacklisted
        except ValueError:
          logging.warn("Error checking domain: " + domain)
          result = False
        return result

    def check_for_benign_domain(self, domain: str) -> bool:
        domainInfo = tldextract.extract(domain)
        root = '{}.{}'.format(domainInfo.domain, domainInfo.suffix).lower()
        
        if domainInfo.suffix in self.whitelist:
            return True

        with open(os.path.join(__location__, 'whitelist.json')) as json_file:
            whitelist = json.load(json_file)
            whitelist = self.list_lower(whitelist)

            if domain in whitelist or root in whitelist:
                return True

            alternatives = self.get_domain_variations(root)
            if 'www' not in domain:
                alternatives += self.get_domain_variations(domain)

            for url in alternatives:
                if url in whitelist:
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
            label = self.label(domain.lower())
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
