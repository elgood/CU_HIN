# IP-to-IP matrix for CU HIN class project
# Campbell


# import libraries
import argparse
import pandas as pd


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

    print(ip2ip.head())


main()
