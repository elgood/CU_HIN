import argparse
import pandas as pd
import scipy.sparse as sp
from dataprun import GenerateWL
import logging


def ip_to_ipNetflow(ip2index: dict, filenames: list):
    '''
    Ip_to_ipNetflow.py is used as an analysis tool to compare HINDOM pruning with Netflow  

    Arguments:
    ip2index: dict - Mapping  
    filenames: list - The files with the netflow.

    Example: 
    python ip_to_ipNetflow.py --dns_files /data/dns/2021-04-10_dns.00:00:00-01:00:00.log 
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
            ip2ip = ip2ip.concat(more)                              # Production dataframe

    indices = []
    for index, row in ip2ip.iterrows():
      if row['src'] not in ip2index or row['dest'] not in ip2index:
        indices.append(index)
    
    # Save for analysis
    ip2ipNF = ip2ip                                                 # Analysis dataframe
    
    lenbefore = len(ip2ip)
    ip2ip = ip2ip.drop(indices) 
    logging.info("Kept " + str(float(100* len(ip2ip))/lenbefore)  + 
                 "% of netflow rows.")
    
    # Convert to integers
    ip2ip['srcInteger'] = ip2ip['src'].map(ip2index)                # Map IP's to index values
    ip2ip['destInteger'] = ip2ip['dest'].map(ip2index)              # " " "
    ip2ip = ip2ip.astype({'srcInteger': int, 'destInteger': int})   # Convert to integers      

    
    # Find and count number of occurrences of repeated IP pairs 
    pairindex = ip2ip.groupby(['src', 'dest']).indices
    paircount = {k: len(v) for k, v in pairindex.items()}

    # Extracting src, dest, counts
    xypair = list(paircount.keys())
    cols = [i[0] for i in xypair]                 # Setting src/'x' to be column
    rows = [i[1] for i in xypair]                 # Setting dest/'y' to be row
    vals = list(paircount.values())               # Values

    dfPROD = pd.DataFrame(vals,columns=['size']) 
    #print('head', dfPROD.head())
    dfPRODprint = dfPROD[dfPROD['size'] > 1]['size']
    dfPRODprint.to_csv('PRODqc.csv')    
    
    ####  Analysis  ####
    #print('Input dataframe before pruning - raw Netflow:')
    #print(ip2ipNF.head(10))
    print('Number of rows in Input dataframe - raw netflow:',len(ip2ipNF.index))
    
    #print('Production dataframe after Prune dictionary filter: ')
    #print(ip2ip.head(10))
    print('Number of rows in Production dataframe:         ',len(ip2ip.index))

    # Find and count number of occurrences of repeated Netflow IP pairs 
    pairindex = ip2ipNF.groupby(['src', 'dest']).indices
    paircount = {k: len(v) for k, v in pairindex.items()}
    print('Number of repeated pairs in input Netflow logs: ', len(paircount))
    qcdf = ip2ipNF.groupby(ip2ipNF.columns.tolist(),as_index=False).size().sort_values(by=['size'],ascending=False)
    print('Number of repeated src to dest pairs, non-"1" : ',qcdf[qcdf['size'] > 1].shape[0]) 
    print('Number of repeated src to dest pairs, "1"     : ',qcdf[qcdf['size'] == 1].shape[0]) 
    print('Most communicative pair, per Netflow samp rate: ',max(qcdf['size']))
    print('Mean of non-"1" pairings  :                     ',qcdf[qcdf['size'] > 1].mean())
    print('Std of non-"1" pairings   :                     ',qcdf[qcdf['size'] > 1].std())
    print('Median of non-"1" pairs   :                     ',qcdf[qcdf['size'] > 1].median()) 
    
    # Extract pairs that occur more than 1 time
    #print(qcdf.head(10)) 
    qcdfprint = qcdf[qcdf['size'] > 1]['size']
    qcdfprint.to_csv('qc.csv') 

    # Compare Prune results with Netflow to compare how communucative potential malicious ip's talk
    #print('Prune dictionary:', ip2index.keys())
    #print('Netflow dataframe: ',ip2ipNF[['src', 'dest']] )
    print('Number of unique Src IPs from Netflow     :     ', len(ip2ipNF['src'].unique()))
    print('Number of unique Dest IPs from Netflow    :     ', len(ip2ipNF['dest'].unique()))
    temp = ip2ipNF[["src", "dest"]].values.ravel()
    print('Number of unique IPs in total from Netflow:     ', len(pd.unique(temp)))
    print('Number of IPs from Prune dictonary        :     ', len(ip2index)) 

    # Extract unique IPs from Production/Prune and see how many times nefarious communicated
    qcdf2 = pd.merge(ip2ip, ip2ipNF,  how='left', left_on=['src','dest'], right_on = ['src','dest'])
    print(qcdf2.groupby(qcdf2.columns.tolist(),as_index=False).size().sort_values(by=['size'],ascending=False))


if __name__ == '__main__':
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--dns_files", type=str, nargs='+', required=True,
      help="The dns log file(s) to use.")
    parser.add_argument('--netflow_files', type=str, required=True, nargs='+',
                        help='Expects log file from /data/dns directory')

    FLAGS = parser.parse_args()

    RL, domain2index, ip2index =  GenerateWL(FLAGS.dns_files)
    ip_to_ipNetflow(ip2index, FLAGS.netflow_files)
