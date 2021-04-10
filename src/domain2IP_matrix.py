# Domain-to-IP matrix for CU HIN project
# import libraries
from scipy import sparse
from numpy import array
import argparse
import pandas as pd
import scipy.sparse as sp
import time
import dataprun
import logging


def getDomainResolveIpCSR(domain2ip: dict,
                          domain2index: dict,
                          ip2index: dict) -> sp.csr:
  """ Returns the domain resolve IP compressed sparse row matrix

  Arguments:
  domain2ip: dict - Mapping from domains to ip.
  domain2index: dict - Mapping from domain to index.
  ip2index: dict - Mapping from ip to index.

  Return:
  csr matrix representing the domain to ip mapping
  """

  domainMatrixSize = max(domain2index.values()) + 1
  logging.info("Number of domains (possible): " + str(domainMatrixSize))
  ipMatrixSize = max(ip2index.values()) + 1
  logging.info("Number of ips (possible): " + str(ipMatrixSize))

  num_ips = len(ip2index)

  lil=sp.lil_matrix((domainMatrixSize, ipMatrixSize))

  # Create index for the domain and IP dictionaries brought in from dataprun
  for domain in domain2ip:
    domain_index=domain2index[domain]
    for ip in domain2ip[domain]:
      ip_index=ip2index[ip]
      lil[domain_index,ip_index]=1

  csr = lil.tocsr()

  return csr


def main():
  '''
  domain2IP_matrix.py creates the domain to ip csr matrix for hindom project
  Usage: python3 domain2IP_matrix.py --inputfiles /data/dns/2021-03-29_dns.05:00:00-06:00:00.log ...
  Requires: dataprun.py
  '''

  # Process command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('--dns_files', type=str, required=True, nargs='+',
                      help='Expects log file from /data/dns directory')
  FLAGS = parser.parse_args()

  RL, domain2index, ip2index =  dataprun.GenerateWL(FLAGS.dns_files)
  domain2ip = GenerateDomain2IP(RL, domain2index)

  # Create sparse matrix of domain to IP relations
  getDomainResolveIpCSR(domain2ip, domain2index, ip2index)


if __name__ == '__main__':
    main()

