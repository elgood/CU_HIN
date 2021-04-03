# IP-to-IP matrix for CU HIN project


# import libraries
import argparse
import pandas as pd
import scipy.sparse as sp
import time
import dataprun


def applyPrune(intoPFile):
    LogList = []  
    LogList.append(intoPFile)   
    RL, DD, IPD = dataprun.GenerateWL(LogList)
#    dict1 = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
#    key_to_lookup = 'a'
#    if key_to_lookup in dict1:
#        print("Key exists")
#    else:
#        print("Key does not exist")
#    pass
    return IPD    


def main():
    '''
    ip_to_ip.py creates the ip to ip csr matrix for hindom project
    
    usage: python ip_to_ip.py --inputfile /data/dns/test_2021-03-14_dns.12:00:00-13:00:00.log
    '''

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="Expects log file from /data/dns directory")
    flags = parser.parse_args()

    # Extract SRC and DEST IPs addresses as though from a csv file
    ts = time.time()
    with open(flags.inputfile, 'r') as infile:
        ip2ip = pd.read_csv(infile, sep='\\t', header=(7), usecols=[2, 4], names=['id.orig_h', 'id.resp_h'], engine='python')

    # Extract list of unique IP  addresses
    srcuniq = ip2ip['id.orig_h'].unique()
    destuniq = ip2ip['id.resp_h'].unique()
    print('Unique Src IPs     :  ', len(srcuniq))
    print('Unique Dest IPs    :  ', len(destuniq))

    # Implement pruning 
    applyPrune(flags.inputfile)

    # Create address dictionaries, 'd'
    srcdict = dict(zip(srcuniq, range(len(srcuniq))))
    destdict = dict(zip(destuniq, range(len(destuniq))))
    # Create inverse dictionaries, 'r'
    # invsrcdict = {v: k for k, v in srcdict.items()}
    # invdestdict = {v: k for k, v in destdict.items()}

    # Map back to df
    ip2ip['srcint'] = ip2ip['id.orig_h'].map(srcdict)
    ip2ip['destint'] = ip2ip['id.resp_h'].map(destdict)

    # Count repeat pairs 
    pairindex = ip2ip.groupby(["srcint", "destint"]).indices
    paircount = {k: len(v) for k, v in pairindex.items()}
    print('Pair count    :  ', len(paircount))

    # Extracting src, dest, counts
    xypair = list(paircount.keys())
    cols = [i[0] for i in xypair]        # Setting src/'x' to be column
    rows = [i[1] for i in xypair]        # Setting dest/'y' to be row
    vals = list(paircount.values())      # Values

    # Create Compressed Sparse Row Matrix
    ip2ipmatrix = sp.csr_matrix((vals, (rows, cols)))
    print('Time, seconds      :  ', time.time() - ts)

    print(ip2ipmatrix)

    return ip2ipmatrix

if __name__ == "__main__":
    main()
