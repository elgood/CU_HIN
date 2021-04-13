import argparse
import pandas as pd
import scipy.sparse as sp
from dataprun import GenerateWL
import logging

def createCSR(df):
    '''
    Creates CSR matrix from Pandas dataframe object. Pandas dataframe must contain a
    'src' and 'dest' representing integer values of IPs from a dictionary. 
    Note: no NaN's allowed.
    '''
    
    # Find and count number of occurrences of repeated IP pairs 
    pairindex = df.groupby(['src', 'dest']).indices
    paircount = {k: len(v) for k, v in pairindex.items()}

    # Extracting src, dest, counts
    xypair = list(paircount.keys())
    cols = [i[0] for i in xypair]                 # Setting src/'x' to be column
    rows = [i[1] for i in xypair]                 # Setting dest/'y' to be row
    vals = list(paircount.values())               # Values

    # Create Compressed Sparse Row Matrix
    ip2ipmatrix = sp.csr_matrix((vals, (cols, rows)))

    return ip2ipmatrix


def ip_to_ip(ip2index: dict, filenames: list):
    '''
    Ip_to_ip.py creates the ip to ip csr matrix for hindom project. 

    Arguments:
    ip2index: dict - Mapping from 
    filenames: list - The files with the netflow.

    Example: 
    python ip_to_ip.py --dns_files /data/dns/2021-04-10_dns.00:00:00-01:00:00.log 
                       --netflow_files /data/converted/ft-v05.2021-04-10.000000-0600.csv
    '''
    
    # Extract SRC and DEST IPs addresses as though from a csv file and 
    # create a Pandas dataframe
    filename = filenames[0]
    ip2ip =  pd.read_csv(filename, sep=',', header=0, usecols=[10, 11], 
                            names=['src', 'dest'], engine='python')
 
    for i in range(1, len(filenames)):
        filename = filenames[i]
        with open(filename, 'r') as infile:
            more = pd.read_csv(filename, sep='\\t', header=0, usecols=[10, 11], 
                            names=['src', 'dest'], engine='python')
            ip2ip = ip2ip.concat(more)

    indices = []
    for index, row in ip2ip.iterrows():
      if row['src'] not in ip2index or row['dest'] not in ip2index:
        indices.append(index)
   
    lenbefore = len(ip2ip)
    ip2ip = ip2ip.drop(indices) 
    logging.info("Kept " + str(float(100* len(ip2ip))/lenbefore)  + 
                 "% of netflow rows.")
    
    # Convert to integers
    ip2ip['src'] = ip2ip['src'].map(ip2index) # Map IP's to index values
    ip2ip['dest'] = ip2ip['dest'].map(ip2index) # " " "
    ip2ip = ip2ip.astype({'src': int, 'dest': int}) # Convert to integers      

    # Create CSR 
    ip2ipmatrix = createCSR(ip2ip)

    return ip2ipmatrix


if __name__ == '__main__':
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--dns_files", type=str, nargs='+', required=True,
      help="The dns log file(s) to use.")
    parser.add_argument('--netflow_files', type=str, required=True, nargs='+',
                        help='Expects log file from /data/dns directory')

    FLAGS = parser.parse_args()

    RL, domain2index, ip2index =  GenerateWL(FLAGS.dns_files)
    ip_to_ip(ip2index, FLAGS.netflow_files)
