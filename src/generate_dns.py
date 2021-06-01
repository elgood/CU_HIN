import argparse
import time
import uuid

def create_dns_data(num_malicious, num_examples):

  #fields
  # ts uid id.orig_h id.orig_p id.resp_h id.resp_p proto trans_id rtt query 
  # qclass qclass_name qtype qtype_name rcode rcode_name AA TC RD RA z answers 
  # TTLS rejected

  current_ts = time.time()

  for i in range(num_examples):
    # ts
    values = []
    values.append(str(current_ts + i))

    # uid
    values.append(str(uuid.uuid4()))

    for j in range(len(values)-1):
      print(values[j], end="\t")
    print(values[len(values)-1], end="\n")

def main():
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--num_malicious', type=int, default=5,
    help="Number of malicious domains")
  parser.add_argument('--num_examples', type=int, default=1000,
    help="Number of examples.")
  FLAGS = parser.parse_args()

  create_dns_data(FLAGS.num_malicious, FLAGS.num_examples)

if __name__ == "__main__":
    main()
