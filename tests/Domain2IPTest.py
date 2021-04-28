import unittest
import domain2IP_matrix as d2i

class Tests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    def testDomain(self):
        domain2ip =  {'a1843.g.akamai.net': ['23.48.9.138']}
        domain2index = {'a1843.g.akamai.net':[6]}
        ip2index = {'23.48.9.138':[479]}
        result = d2i.getDomainResolveIpCSR(domain2ip,domain2index,ip2index)
        self.assertEqual(result, 6, 479)

if __name__ == '__main__':
    unittest.main()
