import sys
import socket
import pandas as pd
import scipy.sparse as sci
import argparse

# Resolve the DNS/IP address of a given domain
# data returned in the format: (name, aliaslist, addresslist)

# Returns the first IP that responds
def getIP(d):
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except Exception:
        return False

# Returns Host name for given IP
def getHost(ip):
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        return False

def main()
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="input csv file")
    flags = parser.parse_args()

    with open(flags.inputfile, 'r') as infile:
        domain = pd.read_csv(infile, sep='\\t', header=(7), usecols=[2, 4], names=['id.orig_h', 'id.resp_h'], engine='python')

    destcol = []

    for i in domain['id.resp_h']:
        try:
            result = socket.inet_aton(i)
            hostname = getHost(i)
            destcol.append(hostname)
            #if hostname: print " " + hostname.replace('\'', '' )
        except socket.error:
            ip = getIP(i)
            destcol.append(ip)
            #if ip: print " " + ip.replace('\'', '' )

    domain['dest'] = destcol

    # Create list of unique addresses
    srcrowid = domain['id.orig_h'].unique()
    destcolid = domain['dest'].unique()

    domain['srcid'] = srcrowid
    domain['destid'] = destcolid

    #Count occurrences
    ipdomain = domain.groupby(["id.orig_h", "dest"])
    pairs = {k: len(v) for k, v in ipdomain.items()}
    data = list(pairs.values())

    #Create matrix
    clientmatrix = sp.csr_matrix((data, (domain['srcid'], domain['destid'])))
    return clientmatrix

if __name__ == "__main__":
    main()