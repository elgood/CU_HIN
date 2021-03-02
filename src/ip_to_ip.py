# IP-to-IP matrix for CU HIN project


# import libraries
import argparse
import pandas as pd
import scipy.sparse as sp
import time


def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="The V5 netflow csv file created by 'flow-export -f2'.")
    flags = parser.parse_args()

    # Open csv file
    ts = time.time()
    with open(flags.inputfile, 'r') as infile:
        ip2ip = pd.read_csv(infile, header=None, usecols=[10, 11], names=['srcaddr', 'destaddr'])

    # Create list of unique addresses
    srcuniq = ip2ip['srcaddr'].unique()
    destuniq = ip2ip['destaddr'].unique()
    print('Unique Src IPs     :  ', len(srcuniq))
    print('Unique Dest IPs    :  ', len(destuniq))

    # Create address dictionaries, 'd'
    srcdict = dict(zip(srcuniq, range(len(srcuniq))))
    destdict = dict(zip(destuniq, range(len(destuniq))))
    # Create inverse dictionaries, 'r'
    #invsrcdict = {v: k for k, v in srcdict.items()}
    #invdestdict = {v: k for k, v in destdict.items()}

    # Map back to df
    ip2ip['srcint'] = ip2ip['srcaddr'].map(srcdict)
    ip2ip['destint'] = ip2ip['destaddr'].map(destdict)

    # Count co-occurrences
    pairindex = ip2ip.groupby(["srcint", "destint"]).indices
    paircount = {k: len(v) for k, v in pairindex.items()}
    print('Paircount length   :  ', len(paircount))

    # Extracting src, dest, counts
    xypair = list(paircount.keys())
    cols = [i[0] for i in xypair]        # Setting src/'x' to be column
    rows = [i[1] for i in xypair]        # Setting dest/'y' to be row
    vals = list(paircount.values())      # Values

    # Create Compressed Sparse Row Matrix, 'D'
    ip2ipmatrix = sp.csr_matrix((vals, (rows, cols)))
    print('Time, seconds      :  ', time.time() - ts)


main()
