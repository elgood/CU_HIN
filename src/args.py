import argparse
import logging

def get_default_ArgumentParser(message: str) -> argparse.ArgumentParser:
  """ Returns an argument parser with some common arguments.  It adds for
    * logging - You set the log level with this argument.
  It also adds the default formatter class.

  Arguments:
  message: str - The help message string given to the ArgumentParser
    constructor.

  Returns:
  An argparse.ArgumentParser

  """

  parser = argparse.ArgumentParser(message,
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("--loglevel", help="The log level.",
    choices=["critical", "error", "warning", "info", "debug"],
    default="error")

  return parser

def process_common_arguments(FLAGS) -> None:
  """ Processes the common arguments.

  Arguments:
  FLAGS - The flags that come from parser.parse_args()

  Returns:
  None
  """

  if 'loglevel' in FLAGS:
    if FLAGS.loglevel == "critical":
      logging.basicConfig(level=logging.CRITICAL,
        format="%(levelname)s:%(filename)s.%(funcName)s:%(message)s")
    elif FLAGS.loglevel == "error":
      logging.basicConfig(level=logging.ERROR,
        format="%(levelname)s:%(filename)s.%(funcName)s:%(message)s")
    elif FLAGS.loglevel == "warning":
      logging.basicConfig(level=logging.WARNING,
        format="%(levelname)s:%(filename)s.%(funcName)s:%(message)s")
    elif FLAGS.loglevel == "info":
      logging.basicConfig(level=logging.INFO,
        format="%(levelname)s:%(filename)s.%(funcName)s:%(message)s")
    elif FLAGS.loglevel == "debug":
      logging.basicConfig(level=logging.DEBUG,
        format="%(levelname)s:%(filename)s.%(funcName)s:%(message)s")
    else:
      raise Exception("Unknown debug level: " + str(FLAGS.loglevel))


