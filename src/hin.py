import argparse
from args import get_default_ArgumentParser, process_common_arguments
from dataprun import GenerateWL, GenerateDomain2IP
import logging
from DomainNameSimilarity import getDomainSimilarityCSR

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

  FLAGS = parser.parse_args()
  process_common_arguments(FLAGS)

  logging.info("DNS files: " + str(FLAGS.dns_files))
  logging.info("Netflow files: " + str(FLAGS.netflow_files))

  RL, domain2index, ip2index =  GenerateWL(FLAGS.dns_files)
  domain2ip = GenerateDomain2IP(RL, domain2index)

  numDomains = len(domain2ip) 
  logging.info("Number of domains in domain2ip " + str(numDomains))
  logging.info("Number of domains in domain2index " + str(numDomains))
  logging.info("Number of ips in ip2index " + str(len(ip2index)))


  print("domain2ip", domain2ip)
  domainSimilarityCSR = getDomainSimilarityCSR(domain2index,
                                          domain2ip, 
                                          FLAGS.domain_similarity_threshold) 
  nnz = domainSimilarityCSR.nnz
  total = numDomains * numDomains
  logging.info("% nonzero entries in domain similarity " + 
               str(float(nnz) / total))


if __name__ == '__main__':
  main()
