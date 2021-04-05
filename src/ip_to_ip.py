import argparse
import pandas as pd
import scipy.sparse as sp
import dataprun


def applyPrune(intoPFile):
    '''
    Implements data pruning using dataprun.py
    '''
    try:
       LogList = []  
       LogList.append(intoPFile)   
       RL, DD, IPD = dataprun.GenerateWL(LogList)
       return IPD 
    except:
       print('An exception occurred in dataprun')  


def ip_to_ip():
    '''
    Ip_to_ip.py creates the ip to ip csr matrix for hindom project. Note: convention
    used for CSR matrix is value (rows, cols).
     
    Usage: python ip_to_ip.py --inputfile /data/dns/2021-03-14_dns.12:00:00-13:00:00.log
    
    Requires: dataprun.py
    '''

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help='Expects log file from /data/dns directory')
    flags = parser.parse_args()

    # Extract SRC and DEST IPs addresses as though from a csv file and create a Pandas dataframe
    with open(flags.inputfile, 'r') as infile:
        ip2ip = pd.read_csv(infile, sep='\\t', header=(7), usecols=[2, 4], names=['id.orig_h', 'id.resp_h'], engine='python')

    # Extract list of unique source and destination IP addresses
    srcuniq = ip2ip['id.orig_h'].unique()
    destuniq = ip2ip['id.resp_h'].unique()

    # Apply data pruning to list of IP addresses 
    IPD = applyPrune(flags.inputfile)
    
    # Create inverse dictionary
    # invIPD = {v: k for k, v in IPD.items()}

    # Map IP's that pass prune criteria back to dataframe 
    ip2ip['srcint'] = ip2ip['id.orig_h'].map(IPD)
    ip2ip['destint'] = ip2ip['id.resp_h'].map(IPD)
    ip2ip = ip2ip.dropna()                         # Pruning will create NaN's
    ip2ip = ip2ip.astype({'srcint': int, 'destint': int})
     
    # Find and count number of occurrence of repeated IP pairs 
    pairindex = ip2ip.groupby(['srcint', 'destint']).indices
    paircount = {k: len(v) for k, v in pairindex.items()}

    # Extracting src, dest, counts
    xypair = list(paircount.keys())
    cols = [i[0] for i in xypair]                 # Setting src/'x' to be column
    rows = [i[1] for i in xypair]                 # Setting dest/'y' to be row
    vals = list(paircount.values())               # Values

    # Create Compressed Sparse Row Matrix
    ip2ipmatrix = sp.csr_matrix((vals, (rows, cols)))

    return ip2ipmatrix

if __name__ == '__main__':
    ip_to_ip()
