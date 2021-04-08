import argparse
from args import get_default_ArgumentParser, process_common_arguments



def main():
  message  =("Runs a hetergeneous information network on the supplied data.")
  parser = get_default_ArgumentParser(message)
  parser.add_argument("--dns_files", type=str, nargs='+', required=True,
    help="The dns log file(s) to use.")
  parser.add_argument("--netflow_files", type=str, nargs='+', required=True,
    help="The netflow log file(s) to use.")

  FLAGS = parser.parse_args()
  process_common_arguments(FLAGS)

  print(FLAGS.dns_files)
  print(FLAGS.netflow_files)

if __name__ == '__main__':
  main()
