import argparse
from args import get_default_ArgumentParser, process_common_arguments
from dataprun import GenerateWL, GenerateDomain2IP
import logging
from DomainNameSimilarity import getDomainSimilarityCSR
from ip_to_ip import ip_to_ip
from time import time
from label import Label
from domain2IP_matrix import getDomainResolveIpCSR
from ClientDomain import getClientQueriesDomainCSR

def main():
  message  =("Runs a hetergeneous information network on the supplied data.")
  parser = get_default_ArgumentParser(message)
  parser.add_argument("--dns_files", type=str, nargs='+', required=True,
    help="The dns log file(s) to use.")
  parser.add_argument("--netflow_files", type=str, nargs='+', required=True,
    help="The netflow log file(s) to use.")
  parser.add_argument("--domain_similarity_threshold", type=float, default=0.1,
    help="The threshold to use to determine if a domain similarity is " +
      "represented or zeroed out.")

  # Exclude certain matrices
  parser.add_argument('--exclude_domain_similarity', action='store_true',
    help="If set, will not compute domain similarity.")
  parser.add_argument('--exclude_ip2ip', action='store_true',
    help="If set, will not compute domain similarity.")
  parser.add_argument('--exclude_domain2ip', action='store_true',
    help="If set, will not compute domainResolveIp.")
  parser.add_argument('--exclude_clientQdomain', action='store_true',
    help="If set, will not compute clientQueryDomain.")

  FLAGS = parser.parse_args()
  process_common_arguments(FLAGS)


  logging.info("DNS files: " + str(FLAGS.dns_files))
  logging.info("Netflow files: " + str(FLAGS.netflow_files))

  RL, domain2index, ip2index =  GenerateWL(FLAGS.dns_files)
  print(RL)
  domain2ip = GenerateDomain2IP(RL, domain2index)

  numDomains = len(domain2ip) 
  domainMatrixSize = max(domain2index.values()) + 1
  ipMatrixSize = max(ip2index.values()) + 1
  numIps = len(ip2index)
  logging.info("Number of domains in domain2ip " + str(numDomains))
  logging.info("Number of domains in domain2index " + str(numDomains))
  logging.info("Number of ips in ip2index " + str(numIps))
  logging.info("Domain matrix size: " + str(domainMatrixSize))

  ################## Labels #######################################
  label = Label()
  labels = label.get_domain_labels(domain2index)
  logging.info("Shape of labels: " + str(labels.shape))
 
  ################### Domain similarity ##########################
  if not FLAGS.exclude_domain_similarity:
    time1 = time()
    domainSimilarityCSR = getDomainSimilarityCSR(domain2index,
                                            domain2ip, 
                                            FLAGS.domain_similarity_threshold) 
    logging.info("Time for domain similarity " + str(time() - time1))
    nnz = domainSimilarityCSR.nnz
    total = domainMatrixSize * domainMatrixSize
    logging.info("nonzero entries (" + str(nnz) + "/" + str(total) + 
                 ") in domain similarity " + str(float(100 * nnz) / total) + "%")
  else:
    logging.info("Excluding domain similarity")
    domainSimilarityCSR = None


  #################### ip to ip ###################################
  if not FLAGS.exclude_ip2ip: 
    time1 = time()
    ip2ip = ip_to_ip(ip2index, FLAGS.netflow_files)
    logging.info("Time for ip2ip " + str(time() - time1))
    nnz = ip2ip.nnz
    total = ipMatrixSize * ipMatrixSize
    logging.info("nonzero entries (" + str(nnz) + "/" + str(total) + 
                 ") in ip2ip " + str(float(100 * nnz) / total) + "%")
  else:
    logging.info("Excluding ip2ip")
    ip2ip = None
 

  ################### Domain resolve ip #############################
  if not FLAGS.exclude_domain2ip:
    time1 = time()
    domainResolveIp = getDomainResolveIpCSR(domain2ip, domain2index, ip2index) 
    logging.info("Time for domainResolveIp " + str(time() - time1))
    nnz = domainResolveIp.nnz
    total = ipMatrixSize * domainMatrixSize
    logging.info("nonzero entries (" + str(nnz) + "/" + str(total) + 
                 ") in domainResolveIp " + str(float(100 * nnz) / total) + "%")
  else:
    logging.info("Excluding domainResolveIp")
    domainResolveIp = None

  ################## Client query domain ############################
  if not FLAGS.exclude_clientQdomain:
    time1 = time()
    clientQueryDomain = getClientQueriesDomainCSR(RL, domain2index, ip2index) 
    logging.info("Time for clientQueryDomain " + str(time() - time1))
    nnz = clientQueryDomain.nnz
    total = ipMatrixSize * domainMatrixSize
    logging.info("nonzero entries (" + str(nnz) + "/" + str(total) + 
                 ") in  " + str(float(100 * nnz) / total) + "%")


 

if __name__ == '__main__':
  main()
