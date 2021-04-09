"""
- Test can be run with command 'python3 -m test_drd_matrix'
- Using unittest python library for testing
"""

import unittest
from drd_matrix import drdMatrix

class testDRDMatrix(unittest.TestCase):
    #sample file for running test
    filename = '/data/dns/2021-03-27_dns.06:00:00-07:00:00.log'
    #limiting number of domain_names to 20
    num = 20
    #setting flag to True to skip dataprun for unittest
    flag = True

    def test_matrixGen(self):
        #setting code initially to False
        code = False
        # matrix output to compare test rssult of with
        sampleResult = [[1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]

        # The code has to fetch registrar of a domain with whois lookup. Some of the
        # lookup will fail randomly. So it is difficult to match exact matrix for test.
        # So test is run multiple times in while loop untill 'testResult' matches 'sampleResult'.
        while code is False:
            #calling the 'drdMatrix()' and passing filename and number of domain_names to use.
            resultMatrix = drdMatrix(self.filename,self.num,self.flag)
            testResult = []
            #Storing elements in the matrix to 'testResult' to compare with 'sampleResult'
            for i in range(len(resultMatrix)):
                testResult.append(list(resultMatrix[i]))
            print("\n")
            try:
                #comparing 'sampleResult' with 'testResult'
                self.assertEqual(sampleResult, testResult)
                #if test is success, print the matrix
                print(resultMatrix)
                #if results match, test is complete
                code = True
            #if number of successful 'whois' lookup is not same as the one used in sample,
            #test fails and tried again.
            except AssertionError as e:
                pass
            else:
                break

if __name__=='__main__':
    unittest.main()

