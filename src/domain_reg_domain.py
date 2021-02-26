import argparse
import whois

def getDomainName(filename):
    with open(filename, 'r') as infile:
        domain = infile.readlines()
        domain_name = []
        for i in range(8, len(domain)):
            domain_name.append(domain[i].split('\t')[6])
        domain_name = set(domain_name)
    return domain_name

def whoisLookup(dname):
    for i in dname:
        try:
            domain = whois.query(i)
            if domain:
                print(i+"\t"+domain.registrar+"\n")
            else:
                print("Nothing found for "+ i)
        except (whois.exceptions.FailedParsingWhoisOutput, KeyError) as e:
            pass

def main():

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help="input csv file")
    FLAGS = parser.parse_args()

    known_tld = ['com', 'uk', 'ac_uk', 'ar', 'at', 'pl', 'be', 'biz', 'br', 'ca', 'cc', 'cl', 'club', 'cn', 'co', 'jp', 'co_jp', 'cz', 'de', 'store', 'download', 'edu', 'education', 'eu', 'fi', 'fr', 'id', 'in_', 'info', 'io', 'ir', 'is_is', 'it', 'kr', 'kz', 'lt', 'ru', 'lv', 'me', 'mobi', 'mx', 'name', 'net', 'ninja', 'se', 'nu', 'nyc', 'nz', 'online', 'org', 'pharmacy', 'press', 'pw', 'rest', 'ru_rf', 'security', 'sh', 'site', 'space', 'tech', 'tel', 'theatre', 'tickets', 'tv', 'us', 'uz', 'video', 'website', 'wiki', 'xyz']

    domain_name_unfiltered = getDomainName(FLAGS.inputfile)
    domain_name = []
    for i in domain_name_unfiltered:
        if i.split(".")[-1] in known_tld:
            domain_name.append(i)
        else:
            pass
    whoisLookup(domain_name)

if __name__=="__main__":
    main()
