import unittest
import DomainNameSimilarity as dns


class Tests(unittest.TestCase):
    def testStringMatcherSame(self):
        string1 = "Test"
        string2 = "Test"
        result = dns.stringSimilar(string1, string2)
        self.assertEqual(result, 1.0)

    def testStringMatherDifferent(self):
        string1 = "Test"
        string2 = "This"
        result = dns.stringSimilar(string1, string2)
        self.assertEqual(result, 0.5)

    def testNetworkSimilarNoSharedNetwork(self):
        ip1 = "192.168.10.10"
        ip2 = "111.111.111.111"
        result = dns.similarByNetwork(ip1, ip2)
        self.assertEqual(result, 0.0)

    def testNetworkSimilarSameIP(self):
        ip1 = "192.168.10.10"
        ip2 = "192.168.10.10"
        result = dns.similarByNetwork(ip1, ip2)
        self.assertEqual(result, 1.0)

    def testDomainsTooFarApart(self):
        domain1 = "google.com"
        domain2 = "bbc.co.uk"
        result = dns.domainSimilarityAlgorithm(domain1, domain2)
        self.assertEqual(result, 0.0)

    def testDomainNotFound(self):
        domain1 = "google.com"
        domain2 = "colorado1.com"
        result = dns.domainSimilarityAlgorithm(domain1, domain2)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
