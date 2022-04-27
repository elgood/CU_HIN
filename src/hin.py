import argparse
from args import get_default_ArgumentParser, process_common_arguments
from dataprun import GenerateWL, GenerateDomain2IP
import logging
#from DomainNameSimilarity import getDomainSimilarityCSR
from ip_to_ip import ip_to_ip
from time import time
from label import Label, LabelFiles
from domain2IP_matrix import getDomainResolveIpCSR
from ClientDomain import getClientQueriesDomainCSR
from PathSim import PathSim
from scipy.sparse import csr_matrix
from affinity_matrix import affinity_matrix, converge
from whois_newness import get_domain_newness, calculate_scores, split_kfold
import numpy as np

### apply newness domain score without K-fold
# python3 hin.py --dns_files /data/examples/dns10000.log --netflow_files /data/examples/netflow10000.csv

### not apply newness domain score without K-fold
# python3 hin.py --dns_files /data/examples/dns10000.log --netflow_files /data/examples/netflow10000.csv --exclude_domain_newness

### apply newness domain score with K-fold
# python3 hin.py --dns_files /data/examples/dns10000.log --netflow_files /data/examples/netflow10000.csv --apply_kfold_crossvalidation --num_kfold=2 

def print_nnz_info(M: csr_matrix, name: str):
  """ Prints nnz info
  """
  n = M.shape[0]
  m = M.shape[1]
  nnz = M.nnz
  total = n * m
  percent = float(100 * nnz) / total
  logging.info("nonzero entries (" + str(nnz) + "/" + str(total) + 
               ") in " + name + " " + 
               "{:.4f}".format(percent) + "%")

def main():
  message  =("Runs a hetergeneous information network on the supplied data.")
  parser = get_default_ArgumentParser(message)
  parser.add_argument("--dns_files", type=str, nargs='+', required=True,
    help="The dns log file(s) to use.")
  parser.add_argument("--netflow_files", type=str, nargs='+', required=True,
    help="The netflow log file(s) to use.")
  parser.add_argument("--domain_similarity_threshold", type=float, default=0.5,
    help="The threshold to use to determine if a domain similarity is " +
      "represented or zeroed out.")
  parser.add_argument("--affinity_threshold", type=float, default=0.5,
    help="If affinity is below threshold we set to zero.")

  # Exclude certain matrices
  parser.add_argument('--exclude_domain_similarity', action='store_true',
    help="If set, will not compute domain similarity.")
  parser.add_argument('--exclude_ip2ip', action='store_true',
    help="If set, will not compute domain similarity.")
  parser.add_argument('--exclude_domain2ip', action='store_true',
    help="If set, will not compute domainResolveIp.")
  parser.add_argument('--exclude_clientQdomain', action='store_true',
    help="If set, will not compute clientQueryDomain.")

  parser.add_argument('--mu', type=float, default=0.5,
    help="Mu parameter used to balance between original labels and new info.")
  parser.add_argument('--tol', type=float, default=0.001,
    help="Tolerance parameter that determines when converges is close enough.")

  parser.add_argument('--good', type=str, default=None,
    help="Location of file with good domains.")
  parser.add_argument('--bad', type=str, default=None,
    help="Location of file with bad domains.")

  # Exclude domain newness (NRD) : 04.26.2022
  parser.add_argument('--exclude_domain_newness', action='store_true',
    help="If set, domain newness will not be added to initial labels.")

  # Apply K-fold cross validation : 04.26.2022
  parser.add_argument('--apply_kfold_crossvalidation', action='store_true',
    help="If set, k fold crossvalidation will be executed.")
  parser.add_argument("--num_kfold", type=int, default=5,
    help="Specifies the number of K in K fold cross validation")

  FLAGS = parser.parse_args()
  process_common_arguments(FLAGS)


  logging.info("DNS files: " + str(FLAGS.dns_files))
  logging.info("Netflow files: " + str(FLAGS.netflow_files))

  RL, domain2index, ip2index =  GenerateWL(FLAGS.dns_files)
  #print(RL)
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
  if FLAGS.good is not None and FLAGS.bad is not None:
    label = LabelFiles(FLAGS.good, FLAGS.bad)
  else:
    label = Label()
  labels = label.get_domain_labels(domain2index)
  logging.info("Shape of labels: " + str(labels.shape))
 
  ################## Update Labels according to newness ##########
  # updated : 04.26.2022
  if not FLAGS.exclude_domain_newness:
      labels_newness = get_domain_newness(domain2index)
      print(np.unique(labels_newness[:,0], return_counts=True))
      labels = labels + labels_newness
      logging.info("Shape of labels: " + str(labels.shape))
 
  ################### Domain similarity ##########################
  #if not FLAGS.exclude_domain_similarity:
  #  time1 = time()
  #  domainSimilarityCSR = getDomainSimilarityCSR(domain2index,
  #                                          domain2ip, 
  #                                          FLAGS.domain_similarity_threshold) 
  #  logging.info("Time for domain similarity " + 
  #               "{:.2f}".format(time() - time1))
  #  print_nnz_info(domainSimilarityCSR, "domain similarity")
  #else:
  #  logging.info("Excluding domain similarity")
  #  domainSimilarityCSR = None


  #################### ip to ip ###################################
  if not FLAGS.exclude_ip2ip: 
    time1 = time()
    ip2ip = ip_to_ip(ip2index, FLAGS.netflow_files)
    logging.info("Time for ip2ip " + 
                 "{:.2f}".format(time() - time1))
    print_nnz_info(ip2ip, "ip2ip")
  else:
    logging.info("Excluding ip2ip")
    ip2ip = None
 

  ################### Domain resolve ip #############################
  if not FLAGS.exclude_domain2ip:
    time1 = time()
    domainResolveIp = getDomainResolveIpCSR(domain2ip, domain2index, ip2index) 
    logging.info("Time for domainResolveIp " + 
                 "{:.2f}".format(time() - time1))
    print_nnz_info(domainResolveIp, "domainResolveIp")
  else:
    logging.info("Excluding domainResolveIp")
    domainResolveIp = None

  ################## Client query domain ############################
  if not FLAGS.exclude_clientQdomain:
    time1 = time()
    clientQueryDomain = getClientQueriesDomainCSR(RL, domain2index, ip2index) 
    logging.info("Time for clientQueryDomain " + 
                 "{:.2f}".format(time() - time1))
    print_nnz_info(clientQueryDomain, "clientQueryDomain")


  ################### CNAME ########################################
  cnameCSR = None # Not complete


  ################### Creating metapaths ############################
  if clientQueryDomain is not None:
    time1 = time()
    domainQueriedByClient = clientQueryDomain.transpose()
    domainQueriedBySameClient = domainQueriedByClient * clientQueryDomain
    logging.info("Time to domainQueriedBySameClient " + 
                 "{:.2f}".format(time() - time1))
  else:
    domainQueriedBySameClient = None

  if domainResolveIp is not None:
    time1 = time()
    ipResolvedToDomain = domainResolveIp.transpose()
    domainsShareIp = domainResolveIp * ipResolvedToDomain
    logging.info("Time to create domainShareIp " + 
                 "{:.2f}".format(time() - time1))
  else:
    domainsShareIp = None

  domainsFromSameClientSegment = None # Not done

  if domainResolveIp is not None:
    R = domainResolveIp
    Rt = R.transpose()
    fromSameAttacker = R * Rt * R * Rt
  else:
    fromSameAttacker = None
     
  
 
  ################### Combine Matapaths ############################ 
  timeTotal = time()
  M = csr_matrix((domainMatrixSize, domainMatrixSize))
  #if domainSimilarityCSR is not None:
  #  time1 = time()
  #  M = M + PathSim(domainSimilarityCSR)
  #  logging.info("Time pathsim domainSimilarityCSR " + 
  #               "{:.2f}".format(time() - time1))
  if cnameCSR is not None:
    time1 = time()
    M = M + PathSim(cnamneCSR)
    logging.info("Time pathsim cnameCSR " + 
                 "{:.2f}".format(time() - time1))
  if domainQueriedBySameClient is not None:
    time1 = time()
    M = M + PathSim(domainQueriedBySameClient)
    logging.info("Time pathsim domainQueriedBySameClient " + 
                 "{:.2f}".format(time() - time1))
  if domainsShareIp is not None:
    time1 = time()
    M = M + PathSim(domainsShareIp)
    logging.info("Time pathsim domainShareIp " + 
                 "{:.2f}".format(time() - time1))
  if domainsFromSameClientSegment is not None:
    time1 = time()
    M = M + PathSim(domainsFromSameClientSegment)
    logging.info("Time pathsim domainsFromSameClientSegment " + 
                 "{:.2f}".format(time() - time1))
  if fromSameAttacker is not None:
    time1 = time()
    M = M + PathSim(fromSameAttacker)
    logging.info("Time pathsim fromSameAttacker " + 
                 "{:.2f}".format(time() - time1))
  logging.info("Time to calculate PathSim " + 
                 "{:.2f}".format(time() - time1))


  ################## Creating Affinity Matrix #########################
  time1 = time()
  M = affinity_matrix(M, FLAGS.affinity_threshold)
  logging.info("Time to calculate affinity " + 
                 "{:.2f}".format(time() - time1))
  nnz = M.nnz
  total = domainMatrixSize * domainMatrixSize
  logging.info("nonzero entries (" + str(nnz) + "/" + str(total) + 
                ") in M after affinity " + str(float(100 * nnz) / total) + "%")

 
  index2domain = {v: k for k, v in domain2index.items()}

  ################## Iterating to convergence ########################
  # update : 04.26.2022
  time1 = time()
  print("All preparation finished. Starting convergence.")
  if FLAGS.apply_kfold_crossvalidation:
      kfold = FLAGS.num_kfold
      print("With cross validation with k : {}".format(kfold))
      statistics = []
      # stratified k fold
      skf, X, y = split_kfold(labels, kfold)
      kth = 1
      for train_index, test_index in skf.split(X, y):
          labels_test_removed = labels.copy()
          # remove pre-labels for test dataset
          for i in test_index:
              labels_test_removed[i][0] = 0
              labels_test_removed[i][1] = 0

          F = converge(M, labels_test_removed, FLAGS.mu, FLAGS.tol)
          s = calculate_scores(labels, F, test_index, index2domain)
          statistics.append(s)
          # print
          print("      [KFold #{}] : recall {}, precision {}, accuracy {}, f1_score {}, cover {}".format(kth, s[0], s[1], s[2], s[3], s[4]))
          kth += 1
      statistics = np.array(statistics)
      avr = np.average(statistics, axis=0)
      print("      [Average ] : recall {}, precision {}, accuracy {}, f1_score {}, cover {}".format(avr[0], avr[1], avr[2], avr[3], avr[4]))

  else:
      print("Without cross validation")
      F = converge(M, labels, FLAGS.mu, FLAGS.tol)
      print("Y F domain")
      for i in range(len(F)):
          print(labels[i,:], F[i,:], index2domain[i])

if __name__ == '__main__':
  main()
