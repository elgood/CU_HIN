# IP-to-IP matrix for CU HIN class project
# jaca3214 - Campbell


# import libraries
import argparse
import numpy as np
import pandas as pd


def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="The V5 netflow csv file created by 'flow-export -f2'.")
    flags = parser.parse_args()

    # Open csv file
    with open(flags.inputfile, 'r') as infile:
        dfIp2Ip = pd.read_csv(infile, header=None, usecols=[10, 11])    # 10, 11 are 'srcaddr', 'destaddr'
        print(dfIp2Ip.head())


main()
