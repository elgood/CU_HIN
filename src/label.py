import json
import tldextract
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class Label:

    whitelist = ["gov", "mil"]

    """
    Returns label for domain.

    If domain is on blacklist -> "malicious"
    If domain is on whitelist -> "good"
    If domain is on both blacklist and whitelist -> "malicious"
    If domain is on neither blacklist or whitelist -> "malicious"
    """
    def getDomainLabel(self, domain):
        if (self.isDomainMalicious(domain)):
            return "malicious"
        if (self.isDomainGood(domain)):
            return "good"
        
        return ""

    """
    Check static blacklist to determine if domain is blacklisted
    """
    def isDomainMalicious(self, domain):
        domainInfo = tldextract.extract(domain)
        root = '{}.{}'.format(domainInfo.domain, domainInfo.suffix).lower()
        if domainInfo.suffix in self.whitelist:
            return False

        with open(os.path.join(__location__, 'blacklist.json')) as json_file:
            blacklist = json.load(json_file)

            if root in self.listToLower(blacklist):
                return True

            for url in self.explodeDomain(root):
                if url in blacklist:
                    return True
            
        return False

    """
    Check static whitelist to determine if domain is whitelisted
    """
    def isDomainGood(self, domain):
        domainInfo = tldextract.extract(domain)
        root = '{}.{}'.format(domainInfo.domain, domainInfo.suffix).lower()
        
        if domainInfo.suffix in self.whitelist:
            return True

        with open(os.path.join(__location__, 'whitelist.json')) as json_file:
            whitelist = json.load(json_file)

            if root in self.listToLower(whitelist):
                return True

            for url in self.explodeDomain(root):
                if url in whitelist:
                    return True
        return False

    """
    Make sure variations of domains are tested
    """
    def explodeDomain(self, domain):
        prefixes = ["https://www.", "http://www.", "www."]
        return [prefix + domain for prefix in prefixes]

    """
    Ignore case
    """
    def listToLower(self, list):
        return [domain.lower() for domain in list]


#TODO: If Domain is in both Whitelist and Blacklist, randomally choose if "malicious" or "good"
#TODO: Is Machine Learning being used here the same way it was used in Hindom?
#TODO: Keep updating the whitelist --> continue searching for programatic sources as well
#TODO: Implement threading
#TODO: Optimize lists loads
#TODO: Push test file
#TODO: Change to check blacklist programatically with following package --> Initial attempt with other package had problem was spamhaus and dns
"""   
    # import pydnsbl
    # domain_checker = pydnsbl.DNSBLDomainChecker()
    # return domain_checker.check('example.org').blacklisted

"""
