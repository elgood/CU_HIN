import sys
import socket
import argparse

# Resolve the DNS/IP address of a given domain
# data returned in the format: (name, aliaslist, addresslist)

# Returns the first IP that responds
def getIP(d):
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except Exception:
        return False

# Returns Host name for given IP
def getHost(ip):
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        return False

def main()
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="input csv file")
    flags = parser.parse_args()

    with open(flags.inputfile, 'r') as infile:
        domain = infile.readlines()

    for i in domain:
        try:
            result = socket.inet_aton(i)
            hostname = getHost(i)
            if hostname: print " " + hostname.replace('\'', '' )
        except socket.error:
            ip = getIP(i)
            if ip: print " " + ip.replace('\'', '' )

if __name__ == "__main__":
    main()