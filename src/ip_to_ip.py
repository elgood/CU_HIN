# IP-to-IP matrix for CU HIN project


# import libraries
import argparse
import pandas as pd
import scipy.sparse as sp


def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="The V5 netflow csv file created by 'flow-export -f2'.")
    flags = parser.parse_args()

    # Open csv file
    with open(flags.inputfile, 'r') as infile:
        ip2ip = pd.read_csv(infile, header=None, usecols=[10, 11], names=['srcaddr', 'destaddr'])

    # Create list of unique addresses
    srcuniq = ip2ip['srcaddr'].unique()
    destuniq = ip2ip['destaddr'].unique()

    # Create address dictionaries
    srcdict = dict(zip(srcuniq, range(len(srcuniq))))
    destdict = dict(zip(destuniq, range(len(destuniq))))

    # Map back to df
    ip2ip['srcint'] = ip2ip['srcaddr'].map(srcdict)
    ip2ip['destint'] = ip2ip['destaddr'].map(destdict)

    # Count co-occurrences
    pairindex = ip2ip.groupby(["srcint", "destint"]).indices
    paircount = {k: len(v) for k, v in pairindex.items()}

    # Extracting src, dest, counts
    rows, cols, vals = [], [], []
    for i in range(len(paircount)):
        cols.append(list(paircount.keys())[i][0])    # Setting src/'x' to be column
        rows.append(list(paircount.keys())[i][1])    # Setting dest/'y' to be row
        vals.append(list(paircount.values())[i])

    # Create Compressed Sparse Row Matrix
    ip2ipmatrix = sp.csr_matrix((vals, (rows, cols)))

    print('B I G M A T R I X')


main()
