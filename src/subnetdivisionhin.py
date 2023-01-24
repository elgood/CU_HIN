import os
from datetime import datetime, timedelta
import argparse
import shutil
import subprocess
import time
import re
from cusubnetidentification import subnet_lookup

def create_temp_dirs(pretty_timestamp: str):
  """ Creates temporary directory where intermediate data goes. 
  
  Arguemnts:
  pretty_timestamp: str - A string representation of a timestamp. Used for
    naming things.

  Returns:
  temp_uncompress_path - Path to the uncompressed data.
  temp_compress_path - Path to the compressed data.
  
  """
  #Create temp dirs as needed, to be used for expanding DNS/Netflow data
  print('\nCreating temp directories, if necessary...')
  temp_uncompress_path = os.path.expanduser('~/CU_HIN_temp_uncompressed/' + 
                                            pretty_timestamp + '/')
  print('\nTesting for the existence of ' + temp_uncompress_path + '...')
  if (os.path.isdir(temp_uncompress_path) and 
      os.path.exists(temp_uncompress_path)):
    print('\nTemp Uncompressed temp dir already exists, no need to create it.')
  else:
    os.makedirs(os.path.expanduser(temp_uncompress_path), exist_ok=False)
    print('\nTemp Uncompressed temp dir does not exist, making it now...')
  temp_compress_path = os.path.expanduser(
      f'~/CU_HIN_temp_compressed/{pretty_timestamp}/')
  print('\nTesting for the existence of ' + temp_compress_path + '...')
  if os.path.isdir(temp_compress_path) and os.path.exists(temp_compress_path):
    print('\nTemp Compressed temp dir already exists, no need to create it...')
  else:
    os.makedirs(os.path.expanduser(temp_compress_path), exist_ok=False)
    print('\nTemp Compressed temp dir does not exist, making it now...')

  return temp_uncompress_path, temp_compress_path

def create_output_dir(args):
  """ Creates the output directory, located at ~/subnetdivisionhinOutput/

  Arguments:
  args - The command line arguments.

  Returns:
  start_datetime - When to start
  end_datatime - When to end

  """
  start_datetime = datetime.strptime(args.start_time, "%Y-%m-%d %H:%M:%S")
  print('\nThe specified Analysis start_time is ' + str(start_datetime))
  end_datetime = start_datetime + timedelta(seconds = 
                  (int(args.duration_seconds)))
  print('The specified Analysis end_time is ' + str(end_datetime))
  pretty_timestamp = ('S' + args.start_time[5:10] + 'T' + 
                     args.start_time[11:19] + 'D' + args.duration_seconds)
  temp_output_path = os.path.expanduser('~/subnetdivisionhinOutput/' + 
                       pretty_timestamp + '/')
  print('\nTesting for the existence of ' + temp_output_path + '...')
  if os.path.isdir(temp_output_path) and os.path.exists(temp_output_path):
    print('\nOutput dir already exists, no need to create it...')
  else:
    os.makedirs(temp_output_path, exist_ok=False)
    print('\nOutput dir does not exist, making it now...')

  return start_datetime, end_datetime, temp_output_path


def main():

  parser = argparse.ArgumentParser(
    description="Runs hin.py against a specific timeframe, using real campus" +
      " DNS/Netflow Data. Identifies the Subnets that are responsible " +
      "for querying known and suspected malicious domains. Outputs results" +
      " to ~/subnetdivisionhinOutput")
  parser.add_argument("start_time", 
    help="Provide a start time for analysis. Format (include quotes):" +
      " \"yyyy-mm-dd hh:mm:ss\"")
  parser.add_argument("duration_seconds", 
    help="Enter an int. Warning: analyzing more than a few minutes might " +
      "take a very long time...")
  parser.add_argument("--include_netflow", action="store_true",
    help="If specified, will find associated netflow files.")

  args = parser.parse_args()
  startscripttimer = time.time()

  print('\nHere are the supplied args:')
  print('\nstart_time: ' + args.start_time)
  print('duration_seconds: ' + args.duration_seconds)

  # Create the "pretty" timestamp that will be used for naming things 
  # consistently. S = Start, T = Time, D = Duration
  # This will be used as the directory name for the output, 
  # which ends up in ~/subnetdivisionhinOutput
  pretty_timestamp = ('S' + args.start_time[5:10] + 'T' + 
    args.start_time[11:19] + 'D' + args.duration_seconds)
  print(f'\nCame up with this pretty_timestamp: {pretty_timestamp} ' + 
    '(S=Start, T=Time, D=Duration). This Timestamp will be used for' +
    ' naming temp and output directories.') 

  temp_uncompress_path, temp_compress_path = create_temp_dirs(pretty_timestamp)
  start_datetime, end_datetime, temp_output_path = create_output_dir(args)


  multi_dns_files_required = False
  multi_netflow_files_required = False
  #Determine which log files will be used, based on user input.
  #As the Netflow files are in 15 min chunks, and the DNS logs are in 
  #1 hour chunks, we sometimes need
  #multiple log files to cover the specified time range
  if (int(str(start_datetime)[14:16]) > 00 and 
      int(str(start_datetime)[14:16]) < 15):
    tempminutes = '00'
    if (int(str(start_datetime)[14:16]) + ((int(args.duration_seconds) + 
        int(str(start_datetime)[17:19]))/60) >= 15):
      print('\nThis will require multiple Netflow files, as the specified' +
            ' timeframe encompasses more than a single file of logging...')
      multi_netflow_files_required = True
  elif (int(str(start_datetime)[14:16]) > 15 and 
        int(str(start_datetime)[14:16]) < 30):
    tempminutes = '15'
    if (int(str(start_datetime)[14:16]) + ((int(args.duration_seconds) + 
        int(str(start_datetime)[17:19]))/60) >= 30):
      print('\nThis will require multiple Netflow files, as the specified ' +
            'timeframe encompasses more than a single file of logging...')
      multi_netflow_files_required = True
  elif (int(str(start_datetime)[14:16]) > 30 and 
        int(str(start_datetime)[14:16]) < 45):
    tempminutes = '30'
    if int(str(start_datetime)[14:16]) + ((int(args.duration_seconds) + int(str(start_datetime)[17:19]))/60) >= 45:
      print('\nThis will require multiple Netflow files, as the specified timeframe encompasses more than a single file of logging...')
      multi_netflow_files_required = True
  else:
    tempminutes = '45'
    if (int(str(start_datetime)[14:16]) + ((int(args.duration_seconds) + int(str(start_datetime)[17:19]))/60)) >= 60:
      print('\nThis will require multiple DNS log files, as the specified timeframe encompasses more than a single file of logging...')
      multi_dns_files_required = True
      print('\nThis will require multiple Netflow files, as the specified timeframe encompasses more than a single file of logging...')
      multi_netflow_files_required = True 

  #Figure out if we need to use multiple DNS log files
  tempdnsfilename = (str(start_datetime)[:10] + '_dns.' + 
    str(start_datetime)[11:13] + ':00:00-' + 
    ("{:02}".format(int(str(start_datetime)[11:13]) + 1)) + ':00:00.log.gz')
  if multi_dns_files_required == True:
    tempdnsfilename_supp = (str(start_datetime)[:10] + '_dns.' + 
      ("{:02}".format(int(str(start_datetime)[11:13]) + 1)) + 
      ':00:00-' + ("{:02}".format(int(str(start_datetime)[11:13]) + 2)) + 
      ':00:00.log.gz')
    tempdns_supp_fullpath = '/data/dns/' + tempdnsfilename_supp
  tempdns_fullpath = '/data/dns/' + tempdnsfilename
  print('\nBased on user input, the DNS log file that will be used: ' + 
        tempdns_fullpath)
  if multi_dns_files_required == True:
    print('This is the supplemental DNS log file that will be used: ' + 
          tempdns_supp_fullpath)
  
  if args.include_netflow:
    #Figure out if we need to use multiple Netflow files
    tempnetflowfilename = ('ft-v05.' + str(start_datetime)[:10] + '.' + 
      str(start_datetime)[11:13] + tempminutes + '00' + '-0600')
    if os.path.exists('/data/' + tempnetflowfilename):
      tempnetflow_fullpath = '/data/' + tempnetflowfilename
      print('\nBased on user input, the Netflow file that will be used: ' + 
            tempnetflow_fullpath)
      if multi_netflow_files_required == True:
        if tempminutes == '45':
          tempnetflowfilename_supp = ('ft-v05.' + str(start_datetime)[:10] + 
            '.' + str(int(str(start_datetime)[11:13]) + 1) + '0000' + '-0600')
        else:
          tempnetflowfilename_supp = ('ft-v05.' + str(start_datetime)[:10] + 
            '.' + str(start_datetime)[11:13] + str(int(tempminutes) + 15) + 
            '00' + '-0600')
        tempnetflow_supp_fullpath = '/data/' + tempnetflowfilename_supp
    else:
      tempnetflowfilename = ('ft-v05.' + str(start_datetime)[:10] + '.' + 
        str(start_datetime)[11:13] + tempminutes + '01' + '-0600')
      tempnetflow_fullpath = '/data/' + tempnetflowfilename
      print('\nBased on user input, the Netflow file that will be used: ' + 
            tempnetflow_fullpath)
      if multi_netflow_files_required == True:
        tempnetflowfilename_supp = ('ft-v05.' + str(start_datetime)[:10] + '.' + 
          str(start_datetime)[11:13] + str(int(tempminutes) + 15) + '01' + 
          '-0600')
        tempnetflow_supp_fullpath = '/data/' + tempnetflowfilename_supp
    if multi_netflow_files_required == True:
      print('This is the supplemental Netflow file that will be used: ' + 
            tempnetflow_supp_fullpath)

  #Copy DNS/Netflow files to the temp folder created in user's home directory
  print('\nCopying DNS log files...')
  shutil.copy(tempdns_fullpath, temp_compress_path)
  if multi_dns_files_required == True:
    shutil.copy(tempdns_supp_fullpath, temp_compress_path)

  if args.include_netflow:
    print('\nCopying Netflow files...')
    shutil.copy(tempnetflow_fullpath, temp_compress_path)
    if multi_netflow_files_required == True:
      shutil.copy(tempnetflow_supp_fullpath, temp_compress_path)

  #Use 'gunzip' and 'flow-export' bash commands to expand data files to the temp directories that were just created
  print('\nExpanding DNS files...')
  temp_bash_string = ('gunzip -c ' + temp_compress_path + tempdnsfilename + 
    ' > ' + temp_uncompress_path + tempdnsfilename[:-3])
  subprocess.call(temp_bash_string, shell=True)
  if multi_dns_files_required == True:
    temp_bash_string_supp = ('gunzip -c ' + temp_compress_path + 
      tempdnsfilename_supp + ' > ' + temp_uncompress_path + 
      tempdnsfilename_supp[:-3])
    subprocess.call(temp_bash_string_supp, shell=True)  

  if args.include_netflow:
    print('\nExpanding Netflow files...')
    temp_bash_string = ('flow-export -f2 < ' + temp_compress_path + 
      tempnetflowfilename + ' > ' + temp_uncompress_path + 
      tempnetflowfilename + ".csv")
    subprocess.call(temp_bash_string, shell=True)
    if multi_netflow_files_required == True:
      temp_bash_string_supp = ('flow-export -f2 < ' + temp_compress_path + 
        tempnetflowfilename_supp + ' > ' + temp_uncompress_path + 
        tempnetflowfilename_supp + ".csv")
      subprocess.call(temp_bash_string_supp, shell=True)

  #Remove headers and footers from data files as needed
  print('\nPreparing data files by removing header and footer lines...')
  
  #opens the DNS file, skips the headers, and writes out a new file
  with open((temp_uncompress_path + tempdnsfilename[:-3]), 'r') as f:
    lines = f.readlines()[8:]
    lines = lines[:-1]
    with open(temp_uncompress_path + 'temp_dns_expand.log', 'w', encoding='UTF8', newline='') as f1:
      for line in lines:
          f1.write(line)
  #If multi_dns_files_required == True, append the second log to temp file, after removing headers/footers
  if multi_dns_files_required == True:
    with open((temp_uncompress_path + tempdnsfilename_supp[:-3]), 'r') as f:
      lines = f.readlines()[8:]
      lines = lines[:-1]
      with open(temp_uncompress_path + 'temp_dns_expand.log', 'a', encoding='UTF8', newline='') as f1:
        for line in lines:
            f1.write(line)

  if args.include_netflow:
    #opens the Netflow file, skips the header, and writes out a new file
    with open((temp_uncompress_path + tempnetflowfilename + '.csv'), 'r') as f:
      lines = f.readlines()[1:]
      with open(temp_uncompress_path + 'temp_netflow_expand.csv', 'w', encoding='UTF8', newline='') as f1:
        for line in lines:
            f1.write(line)
    #If multi_netflow_files_required == True, append the second log to temp file, after removing headers/footers
    if multi_netflow_files_required == True:
      with open((temp_uncompress_path + tempnetflowfilename_supp + '.csv'), 'r') as f:
        lines = f.readlines()[1:]
        with open(temp_uncompress_path + 'temp_netflow_expand.csv', 'a', encoding='UTF8', newline='') as f1:
          for line in lines:
            f1.write(line)

  #Pick out only the log lines within the specified timeframe, and store them in a new file
  print('\nIsolating the log lines that are within the specified timeframe...')
  #opens the temp DNS file
  with open((temp_uncompress_path + 'temp_dns_expand.log'), 'r') as f:
    lines = f.readlines()
    #Somewhere around here, put a test check if nothing is ever added to the file 'dns_expand.log',
    #which would indicate that no malicious domains were found
    with open(temp_uncompress_path + 'dns_expand.log', 'w', encoding='UTF8', newline='') as f1:
      for line in lines:
          temp_epochtime = int(line[:10])
          #print('this is the current line\'s epoch time: ' + str(temp_epochtime))
          temp_datetime = datetime.fromtimestamp(temp_epochtime)
          #print('the current line\'s epoch time, converted to a datetime: ' + str(temp_datetime))
          if ((temp_datetime >= start_datetime) and (temp_datetime < end_datetime)):
            #print('the current line falls within the specified timeframe, and will be analyzed')
            f1.write(line)

  if args.include_netflow:
    #opens the temp Netflow file
    with open((temp_uncompress_path + 'temp_netflow_expand.csv'), 'r') as f:
      lines = f.readlines()
      with open(temp_uncompress_path + 'netflow_expand.csv', 'w', encoding='UTF8', newline='') as f1:
        for line in lines:
            temp_epochtime = int(line[:10])
            #print('this is the current line\'s epoch time: ' + str(temp_epochtime))
            temp_datetime = datetime.fromtimestamp(temp_epochtime)
            #print('the current line\'s epoch time, ' + str(temp_epochtime) + 'converted to a datetime: ' + str(temp_datetime))
            if ((temp_datetime >= start_datetime) and (temp_datetime < end_datetime)):
              #print('the current line falls within the specified timeframe, and will be analyzed')
              f1.write(line)

  #Now that we have our prepared DNS and Netflow files, actually execute hin.py, using the newly generated DNS/Netflow files as input.
  #Output to file 'output.log' in the output dir
  temp_bash_string = ('python hin.py --loglevel debug --dns_files ' + 
    temp_uncompress_path + 'dns_expand.log ' )
  if args.include_netflow:
    temp_bash_string += (' --netflow_files ' + temp_uncompress_path + 
      'netflow_expand.csv ')
  temp_bash_string += ('--affinity_threshold 0.1 --exclude_ip2ip > ' +
       temp_uncompress_path + 'output.log')
  print('\nAbout to run this bash command:\n')
  print(temp_bash_string)
  time.sleep(15)
  subprocess.call(temp_bash_string, shell=True)

  #Read through the output file generated by hin.py. Select the lines that were deemed malicious, and output them to 'positive_hits.output'
  with open((temp_uncompress_path + 'output.log'), 'r') as f:
    lines = f.readlines()
    with open((temp_output_path + 'positive_hits.output'), 'w', encoding='UTF8', newline='') as f1:
      for line in lines:
        #print('comparing against ' + line[0:3])
        if (line[0:3] == '[1.'):
          f1.write(line)
    #Add script timer to output
    with open((temp_output_path + 'positive_hits.output'), 'a', encoding='UTF8', newline='') as f1:
      endoperationimer = time.time()
      f1.write(("\nTotal Execution Time:" + str(timedelta(seconds=(endoperationimer-startscripttimer))) + "\n"))

  #Process the output, correlating True Positives with their associated client subnet by calling the subnet_lookup function from cusubnetidentification.py
  detected_malicious_domains = []
  with open((temp_output_path + 'positive_hits.output'), 'r', encoding='UTF8', newline='') as f:
    lines = f.readlines()
    for line in lines:
      detected_malicious_domains.append((line.split("]", 2)[-1]).strip())
  #Remove the blank line, and script timer at the end of output file
  detected_malicious_domains = detected_malicious_domains[:-2]

  if detected_malicious_domains:
  #For each detected malicious domain, run through the DNS log and store clients that queried aforementioned domain
    temp_identified_clients = []
    with open((temp_uncompress_path + 'dns_expand.log'), 'r') as f:
      lines = f.readlines()
      for dmd in detected_malicious_domains:
        temp_identified_clients = []
        for line in lines:
          temp_client = (re.split(r'\t+', line)[2])
          temp_dest = (re.split(r'\t+', line)[9])
          if temp_dest == dmd:
            if temp_client not in temp_identified_clients:
              temp_identified_clients.append(temp_client)
        temp_text = '\nThe detected malicious domain ' + dmd + ' was queried by these clients during the specified timeframe ' + pretty_timestamp + ':' + str(temp_identified_clients) + '\n'
        print(temp_text)
        temp_text_detail = '\nSubnet lookup info: '
        for tic in temp_identified_clients:
          temp_subnet_lookup_result = str(subnet_lookup(tic))
          if temp_subnet_lookup_result == 'None':
            temp_text_detail = temp_text_detail + 'No subnet information available\n'
          else:
            temp_text_detail = temp_text_detail + temp_subnet_lookup_result + '\n'
        print(temp_text_detail)
        with open(temp_output_path + 'identified_clients.output', 'a', encoding='UTF8', newline='') as f:
          f.write(temp_text)
        with open(temp_output_path + 'identified_clients.output', 'a', encoding='UTF8', newline='') as f:
          f.write(temp_text_detail)
  else:
      print('\nNo malicious domains were detected, so subnet analysis can\'t be done...')


  

  #DO LAST

  #Clean up temp stuff--Delete temp compress and uncompress folders
  print('\nCleaning up temp files...')
  temp_bash_string = 'rm -rf ' + temp_compress_path
  subprocess.call(temp_bash_string, shell=True)
  temp_bash_string = 'rm -rf ' + temp_uncompress_path
  subprocess.call(temp_bash_string, shell=True)


  endscripttimer = time.time()
  print("\nTotal Run Time:" + str(timedelta(seconds=(endscripttimer-startscripttimer))))


main()



