import argparse
import time
import uuid
import random
import socket
import struct
import logging

A_RECORD = "A"
DNS_IP = "125.125.125.125"
DNS_PORT = 53
PROTO_UDP = "udp"
NO_DATA = "-"

def create_random_ip():
  return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def create_domains(prefix: str, n: int):
  """
  Arguments:
  prefix: string - The prefix for all the domains created.
  n - How many domains to create.

  Returns:
  A list with all the domains
  """
  s = [] 
  for i in range(n):
    s.append(prefix + str(i))

  return s

def create_ips(n: int):
  """
  Arguments:
  n: int - How many ips to create.
  
  Returns:
  A list with ips.
  """

  s = [] 
  for i in range(n):
    s.append(create_random_ip())

  return s
  

def create_mapping(s1: set, s2: set):
  assert(len(s1) == len(s2))

  d = {}
  for i in range(len(s1)):
    d[s1[i]] = s2[i]

  return d

def create_dns_data(num_malicious_domains, num_benign_domains, 
                    num_normal_ips, num_infected_ips,
                    num_examples):
  """

  Arguments:
  num_malicious_domains: int - The number of malicious domains.
  num_benign_domains: int - The number of benign domains.
  num_normal_ips: int - The number of ips making requests that are not 
    infected.
  num_infected_ips: int - The number of ips making requests that are
    infected.
  num_examples: int - How many records to make.

  """

  #fields
  # ts uid id.orig_h id.orig_p id.resp_h id.resp_p proto trans_id rtt query 
  # qclass qclass_name qtype qtype_name rcode rcode_name AA TC RD RA z answers 
  # TTLS rejected

  normal_ips = create_ips(num_normal_ips)
  infected_ips = create_ips(num_infected_ips)
  good_domains = create_domains("good", num_benign_domains)
  bad_domains = create_domains("bad", num_malicious_domains)
  good_ips = create_ips(num_benign_domains)
  bad_ips = create_ips(num_malicious_domains)
  good_domain2ip = create_mapping(good_domains, good_ips)
  bad_domain2ip = create_mapping(bad_domains, bad_ips)


  frac_bad = float(num_infected_ips) / float(num_infected_ips + num_normal_ips) 

  current_ts = time.time()

  for i in range(num_examples):

    # Determine if the client is normal or infected
    if random.random() < frac_bad: # infected client
      index = random.randrange(0, num_infected_ips)
      client = infected_ips[index] 
      if random.random() < 0.5: # malicious request
        index = random.randrange(0, num_malicious_domains)
        domain = bad_domains[index]
        answer = bad_domain2ip[domain]

      else: # benign request
        index = random.randrange(0, num_benign_domains)
        domain = good_domains[index]
        answer = good_domain2ip[domain]
        
    else:
      index = random.randrange(0, num_normal_ips)
      client = normal_ips[index]
      index = random.randrange(0, num_benign_domains)
      domain = good_domains[index]
      answer = good_domain2ip[domain]


    #1 ts
    values = []
    values.append(str(current_ts + i))

    #2 uid
    values.append(str(uuid.uuid4()))

    #3 id.orig.h
    values.append(client)

    #4 id.orig_p
    values.append(random.randrange(49152, 65535))

    #5 id.resp_h
    values.append(DNS_IP)

    #6 id resp_p
    values.append(DNS_PORT)

    #7 proto
    values.append(PROTO_UDP)

    #8 trans_id
    values.append(str(i))

    #9 rtt
    values.append(NO_DATA)

    #10 query
    values.append(domain)

    #11 qclass
    values.append(1)

    #12 qclass_name
    values.append("C_INTERNET")

    #13 qtype
    values.append(1)

    #14 qtype_name
    values.append(A_RECORD)

    #15 rcode
    values.append(0)

    #16 rcode_name
    values.append("NOERROR")

    #17 AA
    values.append("T")

    #18 TC
    values.append("F")

    #19 RD
    values.append("F")

    #20 RA
    values.append("F")

    # z
    values.append(0)

    # answers
    values.append(answer)

    # TTLS
    values.append(3600.0)

    # rejected
    values.append("F")

    for j in range(len(values)-1):
      print(values[j], end="\t")
    print(values[len(values)-1], end="\n")

def main():
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--num_malicious_domains', type=int, default=5,
    help="Number of malicious domains")
  parser.add_argument('--num_benign_domains', type=int, default=100,
    help="Number of malicious domains")
  parser.add_argument('--num_normal_ips', type=int, default=500,
    help="Number of malicious domains")
  parser.add_argument('--num_infected_ips', type=int, default=25,
    help="Number of infected ips")
  parser.add_argument('--num_examples', type=int, default=5000,
    help="Number of examples.")
  FLAGS = parser.parse_args()
  
  create_dns_data(FLAGS.num_malicious_domains, FLAGS.num_benign_domains,
                  FLAGS.num_normal_ips, FLAGS.num_infected_ips,
                  FLAGS.num_examples)

if __name__ == "__main__":
    main()
