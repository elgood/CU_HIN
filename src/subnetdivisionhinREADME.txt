This readme is intended to accompany 'subnetdivisionhin.py' and 'cusubnetidentification.py'

Please first review the main CU_HIN readme file: ‘/CU_HIN/src/README.md’ and enable python virtual environment

usage: subnetdivisionhin.py [-h] start_time duration_seconds

Runs hin.py against a specific timeframe, using real campus DNS/Netflow Data.
Identifies the Subnets that are responsible for querying known and suspected
malicious domains. Outputs results to ~/subnetdivisionhinOutput

positional arguments:
  start_time        Provide a start time for analysis. Format (include
                    quotes): "yyyy-mm-dd hh:mm:ss"
  duration_seconds  Enter an int. Warning: analyzing more than a few minutes
                    might take a very long time...

optional arguments:
  -h, --help        show this help message and exit

Example: python subnetdivisionhin.py "2022-04-22 11:59:55" 10


