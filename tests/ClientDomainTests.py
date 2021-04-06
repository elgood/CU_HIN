import unittest
import ClientDomain as cd

class Tests(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetIP(self):
        domainName = "boulder.colorado.edu"
        ipPart = "128.138"
        IP = cd.getIP(domainName)
        self.assertIn(ipPart,IP)

    def testGetHost(self):
        testIP = "128.138.129.76"
        domainPart = "colorado.edu"
        domainName = cd.getHost(testIP)
        self.assertIn(domainPart,domainName)


if __name__ == '__main__':
    unittest.main()