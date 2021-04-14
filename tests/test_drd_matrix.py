"""
- Test can be run with command 'python3 -m test_drd_matrix'
- Using unittest python library for testing
"""

import unittest
from drd_matrix import csrMatrix

class testDRDMatrix(unittest.TestCase):

    def test_matrixGen(self):

        #sample domainName-index dictionary
        domainNameIndexDictionary = {'datamixer-pa.googleapis.com': 0, 'utcnist.colorado.edu': 2, 'd28je938im599m.cloudfront.net': 3, 'surfside.io': 5, 'scontent.fapa1-2.fna.fbcdn.net': 6, 'control.preyproject.com': 7, 'imp-east.pub.local.emxdgt.com': 8, 'ipmx6.colorado.edu': 9, 's.spoutable.com': 10, 'static.vrv.co': 11, 'www.google.com': 13}

        #sample index list with successful whois lookups
        domainNameIndexList = [0, 3, 5, 6, 7, 8, 10, 11, 13]

        #sample dictionary with domain name Index and corresponding registrar
        domainNameIndex2RegistrarDictionary = {0: 'MarkMonitor Inc.', 3: 'MarkMonitor Inc.', 5: 'Gandi SAS', 6: 'RegistrarSafe, LLC', 7: 'NameCheap, Inc.', 8: 'GoDaddy.com, LLC', 10: 'GoDaddy.com, LLC', 11: 'CCI REG S.A.', 13: 'MarkMonitor Inc.'}

        #Sample data for matrix
        sampleResult = [[1, 1, 0, 0, 0, 0, 0, 0, 1], [1, 1, 0, 0, 0, 0, 0, 0, 1], [0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], [1, 1, 0, 0, 0, 0, 0, 0, 1]]

        #calling the 'drdMatrix()' and passing filename and and flag to skip data pruning.
        resultMatrix = csrMatrix(domainNameIndexList,domainNameIndex2RegistrarDictionary)
        
        #Storing elements in the matrix to 'testResult' in order to compare with 'sampleResult'
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

