import unittest
#Handleing import issue: system-path at runtime
import sys
sys.path.insert(1,"../../src")

import dataprun

class TestSketch(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    #The domain and answer in same line
    def test_SingleLine(self):
        
        RL,DD,IPD = dataprun.GenerateWL(["unittest4C.log"])
        answerDomain  = ["google.com","tmall.com","youtube.com","baidu.com"]
        answerIP = ["0.0.0.0","0.0.0.2","192.168.75.0","192.168.75.2","192.168.75.1","192.168.75.3"]
                
        for domain in DD:
            self.assertIn(domain,answerDomain)
        
        for ip in IPD:
            self.assertIn(ip,answerIP)

        self.assertEqual(len(DD.keys()),len(answerDomain))
        self.assertEqual(len(IPD.keys()),len(answerIP))

        
    def test_PrunEffect(self):
        
        #This setting will removed all inputs 
        RL,DD,IPD = dataprun.GenerateWL(["unittest4C.log"],ka=0,kd=0)
        self.assertEqual(len(DD.keys()),0)
        self.assertEqual(len(IPD.keys()),2)


    #The domain and answers in different line
    def test_DifferentLine(self):
        
        RL,DD,IPD = dataprun.GenerateWL(["unittest4S.log"])
        answerDomain  = ["google.com","tmall.com","youtube.com","baidu.com"]
        answerIP = ["0.0.0.2","0.0.0.0","192.168.75.0","192.168.75.2","192.168.75.1","192.168.75.3"]

        for domain in DD:
            self.assertIn(domain,answerDomain)

        for ip in IPD:
            self.assertIn(ip,answerIP)

        self.assertEqual(len(DD.keys()),len(answerDomain))
        self.assertEqual(len(IPD.keys()),len(answerIP))

    #Invald data
    def test_InvalidInput(self):

        ans = dataprun.GenerateWL(["unittest4I.log"])
        self.assertIs(ans,None)

    #Test multiple answers
    def test_MultipleAnswers(self):
        
        RL,DD,IPD = dataprun.GenerateWL(["unittest4MC.log"])
        answerDomain  = ["google.com","tmall.com","youtube.com","baidu.com"]
        answerIP = ["0.0.0.0","0.0.0.2","1.0.0.0","1.0.0.2","192.168.75.0","192.168.75.2","192.168.75.1","192.168.75.3"]
                
        for domain in DD:
            self.assertIn(domain,answerDomain)
        
        for ip in IPD:
            self.assertIn(ip,answerIP)

        self.assertEqual(len(DD.keys()),len(answerDomain))
        self.assertEqual(len(IPD.keys()),len(answerIP))

    #Test Domain to IP mapping
    def test_DomainToIPs(self):
        
        RL,DD,IPD = dataprun.GenerateWL(["unittest4C.log"])
        D2IP = dataprun.GenerateDomain2IP(RL,DD)
        answerDict  = {"google.com":["0.0.0.0"],"tmall.com":["0.0.0.2"],"youtube.com":["0.0.0.0"],"baidu.com":["0.0.0.2"]}
                
        for dd in D2IP:
            self.assertIn(dd,answerDict)
            self.assertEqual(D2IP[dd],answerDict[dd])
        

        self.assertEqual(len(answerDict),len(D2IP))




if __name__ == '__main__':
  unittest.main()
