# Domain-to-IP matrix for CU HIN project
# import libraries
import argparse
import pandas as pd
import scipy.sparse as sp
import time
import dataprun

def applyPrune(intoPFile):
    # Implements datapruning
    LogList = []  #argument to ReadInLogs function in dataprun
    LogList.append(intoPFile)
    RL, DD, IPD = dataprun.GenerateWL(LogList)
    return IPD

def main():
    '''
    domain2IP_matrix.py creates the ip to ip csr matrix for hindom project
    Usage: python3 domain2IP_matrix.py --inputfile /data/dns/2021-03-29_dns.05:00:00-06:00:00.log
    Requires: dataprun.py
    '''

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help='Expects log file from /data/dns directory')
    flags = parser.parse_args()

       # Implement pruning
    IPD = applyPrune(flags.inputfile)

    LogList = []  #argument to ReadInLogs function in dataprun
    LogList.append(flags.inputfile)
    RL, DD, IPD = dataprun.GenerateWL(LogList)

    num_domains=len(DD)
    num_ips=len(IPD)

    lil=sp.lil_matrix((num_domains,num_ips))

    for domain in RL:
        domain_index=DD[domain]
        for ip in RL[domain]:
            #print("ip="+ip)
            ip_index=IPD[ip]
            lil[domain_index,ip_index]=1


    csr1=lil.tocsr()
    print(csr1)

    print(DD)
    print('----------------')


    return csr1

if __name__ == '__main__':
    main()

