import sys
import socket
import scipy.sparse as sci
from scipy.sparse import csr_matrix
import argparse
from dataprun import GenerateWL
from time import time



def getClientQueriesDomainCSR(responseLog: dict,
                              domain2index: dict,
                              ip2index: dict) -> sci.csr:
  """ Returns compressed sparse row of which clients queried which domains.
  
  Arguments:
  responseLog: dict - The response log dictionary from data pruning code.
 
  Return:
  compressed sparse row matrix
  """
  
  maxIp     = max(ip2index.values()) + 1
  maxDomain = max(domain2index.values()) + 1
  lol = sci.lil_matrix((maxIp, maxDomain))  

  for domain in responseLog:
    for client in responseLog[domain]:
      ipIndex     = ip2index[client]
      domainIndex = domain2index[domain]
      lol[ipIndex, domainIndex] += 1

  return lol.tocsr()



def updateClientQueriesDomainCSR(filenames: list, domain2index: dict,
                              ip2index: dict) -> sci.csr:
    """ Returns compressed sparse row of how many times each clients queried each domains.

    Arguments:
    filenames: list of files to read data in from.
    domain2index: list of valid domains from file
    ip2index: list of valid clients from file

    Return:
    updated compressed sparse row matrix
    """
    inputfile = filenames[0]
    maxIp = max(ip2index.values()) + 1
    maxDomain = max(domain2index.values()) + 1
    lol = sci.lil_matrix((maxIp, maxDomain))

    # update matrix with multiple queries if exists
    with open(inputfile, "r") as log:

        subdata = log.readlines()
        for line in subdata:

            if (line[0] == "#"):
                continue  # ignore first line

            dline = line.strip().split("\t")  # require given format, otherwise throw exception
            tempClient = dline[2]
            tempDomain = dline[9]

            clientMarker = ""
            domainMarker = ""

            if tempClient in ip2index:
                tempipIndex = ip2index[tempClient]
                clientMarker = "Y"
            if tempDomain in domain2index:
                tempdomainIndex = domain2index[tempDomain]
                domainMarker = "Y"
            if (clientMarker == "Y" and domainMarker == "Y"):
                lol[tempipIndex, tempdomainIndex] += 1

    return lol.tocsr()



# Resolve the DNS/IP address of a given domain
# data returned in the format: (name, aliaslist, addresslist)
# Returns the first IP that responds for Passive DNS
def getIP(d):
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except Exception:
        return False

# Returns Host name for given IP for Passive DNS
def getHost(ip):
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        return False



def main():
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputtxtfile', type=str, required=True,
                        help="input text file")
    flags = parser.parse_args()

    filenames = []
    filenames.append(flags.inputtxtfile)

    readlog, domain2index, ip2index = GenerateWL(filenames)

    # Passive DNS for domains
    for i in domain2index:
        try:
            result = socket.inet_aton(i)
            hostname = getHost(i)
            if hostname:
                print(i + ": " + hostname.replace('\'', ''))
        except socket.error:
            ip = getIP(i)
            if ip:
                print(i + ": " + ip.replace('\'', ''))

    # Passive DNS for clients
    for i in ip2index:
        try:
            result = socket.inet_aton(i)
            hostname = getHost(i)
            if hostname:
                print(i + ": " + hostname.replace('\'', ''))
        except socket.error:
            ip = getIP(i)
            if ip:
                print(i + ": " + ip.replace('\'', ''))

    #Create matrix
    time1 = time()
    clientmatrix = updateClientQueriesDomainCSR(filenames, domain2index, ip2index)
    print("Time for clientmatrix " +
          "{:.2f}".format(time() - time1))
    print(clientmatrix)

    if clientmatrix is not None:
        time1 = time()
        domainmatrix = clientmatrix.transpose()
        domainQueriedBySameClient = domainmatrix * clientmatrix
        print("Time to domainQueriedBySameClient " +
                     "{:.2f}".format(time() - time1))
        print(domainQueriedBySameClient)
    else:
        domainQueriedBySameClient = None


if __name__ == "__main__":
    main()
