import re #check valid Domain/String
from datetime import datetime #running time
from ipaddress import ip_address #check valid ip 
import sys #Eception information 
import os 

#Tools 
def ValidDomain(Domain):
    
    """
    Description:
    This function check if the input string is a valid domain name 
    Based on given rules

    Argument: String

    Return: True if it is a valid domain name, False elsewise
    
    """
    
    #Valid Domain
    DomainSize = len(Domain) >= 2 and len(Domain) <= 255 # 2 < Domain length < 255 
    DomainChar = re.search("[^a-zA-Z0-9\.\-]",Domain) == None #Only a-z/A-Z, 0-9,-,.
    DomainFirst = re.search("[a-zA-Z0-9]",Domain[0]) #Only a-zA-Z0-9
    DomainLast = Domain[-1] != "-" and Domain[-1] != "." #Not - or .

    return DomainSize and DomainChar and DomainFirst and DomainLast


def ValidIP(IP):

    """
    Description:
    This function check if the input string is a valid IP address, using 
    ip_address from ipaddress library

    Argument: String

    Return: True if it is a valid IP address, False elsewise
    
    """


    try:
        result = ip_address(IP)
        return True
    except:         #ValueError Exception
        return False

def Answer2IP(Answer):

    """
    Description:
    This function parses the input string from the Answer into list of ip address in strings 

    Argument: String

    Return: List of valid ip address in string, if there is none, return an empty list 
    
    """

    answers = Answer.split(",") #potential multiple ips
    result = [] #<string>
    for a in answers: 
        #check IP addresses                                              
        if(ValidIP(a)):
            result.append(a)

    #print(result)
    return result

#Read in
def ReadInLogs(LogList):

    """
    Description: 
    This function parses the list of input DNS log files and return different dictionary for data pruning  
    
    Argument: List of strings of filename 

    Return:A tuple of following items: 
                                Dictionary RL: Valid Domain<String>:Client<String>:IPList (Answer) <list<String>>
                                Domain Dictionary: Domains<string>:appeared times<int>
                                Client Dictionary: Client<string>: appeared times<int>>
                                IP Dictionary: IP<string>: Domains<list<string>>
                                Total calls: the number of DNS requests

    if expception or error take place, return empty dictionary
 
    
    """

    ReadinLogDict = dict() #MixIdentifier[id.orig_h+id.orig_p+id.resp_h+id.resp_p+trans_id]<String>:List<Strings>[Client,Domain,IPs]
    DomainDict = dict() #Domains<string>:appeared times<int> 
    ClientDict = dict() #Client<string>: appeared times<list<string>>
    IPDict = dict()     #IP<string>: Domain<string>
    RL = dict()             #Record List Store a list of [DOmain,Client,IPs] for build other dictionary
    TotalLine = 0
    ValidLine = 0

    for LogFile in LogList:
        #print(Log)
        Log = os.path.join(LogFile)
        try:
            with open(Log,"r") as LogData:
         
                Data = LogData.readlines()
                print("Inputing {} lines ... ".format(len(Data)))
                for line in Data:

                
                    if(line[0] == "#"):
                        continue #ignore first line

                    #print(line)
                    TotalLine += 1
                    dline = line.strip().split("\t") #require given format, otherwise throw exception
                    IDKey = dline[2]+dline[3]+dline[4]+dline[5]+dline[7]
                    Client = dline[2]
                    Domain = dline[9]
                    IPList = Answer2IP(dline[21])

                    updateFlag = False #determine if can updates
                    
                    if(Domain == "-" and len(IPList) < 1):
                        continue #ignore such log
                    
                    if(IDKey in ReadinLogDict):

                        #update Domian
                        if(ReadinLogDict.get(IDKey)[1] == "-" and ValidDomain(Domain)):
                            ReadinLogDict[IDKey][1] = Domain
                            IPList = ReadinLogDict[IDKey][2]
                            updateFlag = True
                            ValidLine += 2 #need two logs
                            #print("C1-")
                            

                        #update IPs from Answer
                        if(len(ReadinLogDict.get(IDKey)[2]) == 0 and len(IPList) > 0): #at least one valid IP
                            ReadinLogDict[IDKey][2] = IPList
                            Domain = ReadinLogDict[IDKey][1]
                            updateFlag = True
                            ValidLine += 2 #need two logs
                            #print("C2-")
                            

                    else:
                        if((Domain == "-" or ValidDomain(Domain)) and (ValidIP(Client) or dline[21] == "-")): 
                            #Client should be valid; Domain either valid or empty
                            ReadinLogDict[IDKey] = [Client,Domain,IPList]
                            updateFlag = (Domain != "-" and len(IPList) > 0)
                            ValidLine += 1
                            #print("C3")
                             

                    #if both domian and IPs exists, update to other dictoionaries
                    #if(IDKey in ReadinLogDict and not updateFlag):
                        #print(IDKey)
                        #print(ReadinLogDict[IDKey])

                    if(updateFlag):

                        #if(IDKey in ReadinLogDict):
                            #print(IDKey)
                            #print(ReadinLogDict[IDKey])

                        if(Domain not in RL):
                            RL[Domain] = {Client: IPList}

                        elif(Client not in RL.get(Domain)):
                            RL[Domain][Client] = IPList

                        else:
                            RL[Domain][Client] += IPList
                        
                            

                        #Domain
                        if(Domain not in DomainDict):
                            DomainDict[Domain] = 0
                        DomainDict[Domain] += 1
                        

                        #Client    
                        if(Client not in ClientDict):
                            ClientDict[Client] = 0
                        ClientDict[Client] += 1
                    

                        #IPs
                        for ip in IPList:

                            if(ip not in IPDict):
                                IPDict[ip] = []
                            IPDict[ip].append(Domain)

        except IOError as Error:
            print("ERROR: I/O error {} CHECK INPUT FILE NAME AND ADDRESS".format(Error))
        except:
            print("ERROR: {}".format(sys.exc_info()[0]))


    precent = 0
    if(TotalLine != 0): precent = (ValidLine/TotalLine)*100
    print("Read in {} log; {} ({:.3f}%) logs are useful (contain valid domain/client/ips)".format(TotalLine,ValidLine,precent))
    print("Valid Domains: {}\nValid Clients: {}\nValid IPs: {}".format(len(DomainDict),len(ClientDict),len(IPDict)))
    #only retuen cleaned clients,domains.ips
    return (RL,DomainDict,ClientDict,IPDict,TotalLine)


def Prun(DomainDict,ClientDict,IPDict,TotalCall,kd=1,ka=1,kc=1): #defaulr settingska=0.25,kb=0.001,kc=3
   
    """
    Description:
    This function will further remove logs information based on the Hindom paper's requirement
    
    Arguments: parameters for pruning the DNS logs: kd,ka,kc 
    Domain Dictionary: Domains<string>:appeared times<int>
    Client Dictionary: Client<string>: appeared times<int>>
    IP Dictionary: IP<string>: Domains<list<string>>
    Total calls: the number of DNS requests


    Return: A tuple of following items:
    Dictionary of all valid Domains: Domain<String>:index<int>
    Dictionart of all valid Client and Answeres IPs: IP<String>:index<int>

    If an error occur, return None
    """

    #make sure input isn't empty
    if(len(DomainDict) < 1 or len(ClientDict) < 1 or len(IPDict) < 1):
        return None

    MaxDomain = len(DomainDict)*kd #popular domain
    MaxClient = TotalCall*ka  #busy client 

    #print(MaxDomain," ",MaxClient)

    DomainNo = dict()
    #Only IPs and Domain
    IPNo = dict()
    
    #Domain 
    index = 0 #may adjusted
    for domain in DomainDict:

        if(DomainDict.get(domain) < MaxDomain):
            DomainNo[domain] = index
            index += 1
    #Client
    ClientSizeBefore = len(ClientDict) 
    index = 0
    for client in ClientDict:

        cNum = ClientDict.get(client)
        if(cNum < MaxClient and cNum >= kc):
            IPNo[client] = index
            index += 1
    
    ClientSizeAfter = index

    #IP
    IPSizeBefore = len(IPDict)
    IPSizeAfter = 0
    for ip in IPDict:

        if(len(set(IPDict.get(ip))) > 1):
            #print(ip,": ",IPDict.get(ip))
            IPNo[ip] = index
            index += 1
            IPSizeAfter += 1

    #any of the empty dict should no reach here
    dp = (len(DomainNo)/len(DomainDict))*100
    cp = (ClientSizeAfter/ClientSizeBefore)*100
    ipp = (IPSizeAfter/IPSizeBefore)*100

    print("Pruned Data:\nDomain: {} ({:.3f}% remain)\nClient: {}({:.3f}% remain)\nIP: {}({:.3f}% remain)".format(len(DomainNo),dp,ClientSizeAfter,cp,IPSizeAfter,ipp))
    return (DomainNo,IPNo)



def GenerateWL(LogLists,kd=1,ka=1,kc=1,ShowTime=True):

    """
    Description:
    This function act as a wrapper to be generate valid list (Whitelist) of Domains and IPs with Assigned index
    
    Argument: List of input files, parameters from Hindom paper, Flag for print out running time

    Return:  A tuple of following items:
    Dictionary RL: Valid Domain<String>:Client<String>:IPList (Answer) <list<String>>
    Dictionary of all valid Domains: Domain<String>:index<int>
    Dictionary of all valid Client and Answeres IPs: IP<String>:index<int>

    If an error occur, return None
 
    
    """

    
    st = datetime.now()
    RL,DD,CD,IPD,TCalls = ReadInLogs(LogLists)
    et = datetime.now()
    tt = et - st
    print()
    if(ShowTime):print("Read in cost:{}".format(tt))
    #No empty dictionary
    if(len(DD) > 0 and len(CD) > 0 and len(IPD) > 0):
        print()
        print("Data {} Cleaned. Start pruning ... ".format(TCalls))
        st = datetime.now()
        DD,IPD = Prun(DD,CD,IPD,TCalls,kd,ka,kc)
        et = datetime.now()
        tt = et - st
        if(ShowTime):
            print()
            print("Purn cost:{}".format(tt))
        return (RL,DD,IPD)

    else:
        return None
    
def GenerateDomain2IP(RL,DD):
    
    """
    
    Description:
    This function return a dictionary maps the relation on (Answer)IPs  
    
    Argument:
    Dictionary RL: Valid Domain<String>:Client<String>:IPList (Answer) <list<String>>
    Dictionary of all valid Domains: Domain<String>:index<int>


    Return: A dictionary maps Domain to IPs: Domian<Stirng>:IPs<list<String>>
    
    """

    Domain2IP = dict()
    Domains = list(DD.keys())
    IP2Domain = dict()

    #Form IP2D again
    for dd in Domains:
        temp = set(sum(RL[dd].values(),[]))
        for ip in temp:
            if(ip not in IP2Domain):
                IP2Domain[ip] = []
            IP2Domain[ip].append(dd)

    for ip in IP2Domain:

        if(len(IP2Domain[ip]) > 1):
            
            for domain in IP2Domain[ip]:
                if(domain not in Domain2IP):
                    Domain2IP[domain] = []
                Domain2IP[domain].append(ip)

    #Clients
    
    return Domain2IP






