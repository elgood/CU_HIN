"""
- Test can be run with command 'python3 -m test_drd_matrix'
- Using unittest python library for testing
"""

import unittest
from drd_matrix import csrMatrix

class testDRDMatrix(unittest.TestCase):

    def test_matrixGen(self):

        #sample list of domain names
        domainNameList = ['prod.pinterest.global.map.fastly.net', 'r218.em.express.com', 'us3a-collab-powerpoint.officeapplf.live.com.akadns.net', 'a-ups-presence9-prod-azsc.centralus.cloudapp.azure.com', 'pool.ntp.org', 'chtbl.com', 'admin.buildpulse.com', 'vmx-prproxy.mystream2.com', 'skypedataprdcolaus00.cloudapp.net', 'northcarolinajobnetwork.com']

        #sample dictionary with domain name and corresponding registrar
        domainRegistrarDictionary = {'prod.pinterest.global.map.fastly.net': 'MarkMonitor Inc.', 'r218.em.express.com': 'CSC Corporate Domains, Inc.', 'us3a-collab-powerpoint.officeapplf.live.com.akadns.net': 'Akamai Technologies, Inc.', 'a-ups-presence9-prod-azsc.centralus.cloudapp.azure.com': 'MarkMonitor Inc.', 'pool.ntp.org': 'Tucows Domains Inc.', 'chtbl.com': 'NameCheap, Inc.', 'admin.buildpulse.com': 'Namespro Solutions Inc.', 'vmx-prproxy.mystream2.com': 'GoDaddy.com, LLC', 'skypedataprdcolaus00.cloudapp.net': 'MarkMonitor Inc.', 'northcarolinajobnetwork.com': 'eNom, LLC'}

        #Sample data for matrix
        sampleResult = [[1, 0, 0, 1, 0, 0, 0, 0, 1, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0, 0], [1, 0, 0, 1, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]
        
        #calling the 'drdMatrix()' and passing filename and and flag to skip data pruning.
        resultMatrix = csrMatrix(domainNameList,domainRegistrarDictionary)
        
        #Storing elements in the matrix to 'testResult' to compare with 'sampleResult'
        testResult = []
        for i in range(len(resultMatrix)):
            testResult.append(list(resultMatrix[i]))
        
        #comparing 'sampleResult' with 'testResult'
        self.assertEqual(sampleResult, testResult)
        
        #if test is success, print the matrix
        #if results match, test is complete
        print("\n")
        print(resultMatrix)

if __name__=='__main__':
    unittest.main()

