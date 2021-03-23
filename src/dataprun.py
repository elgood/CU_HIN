import re #check valid Domain/String
from datetime import datetime #running time
from ipaddress import ip_address #check valid ip 
import sys #Eception information 

#True if data is valid
def ValidDomain(Domain):
    
    #Valid Domain
    DomainSize = len(Domain) >= 2 and len(Domain) <= 255 # 2 < Domain length < 255 
    DomainChar = re.search("[^a-zA-Z0-9\.\-]",Domain) == None #Only a-z/A-Z, 0-9,-,.
    DomainFirst = re.search("[a-zA-Z0-9]",Domain[0]) #Only a-zA-Z0-9
    DomainLast = Domain[-1] != "-" and Domain[-1] != "." #Not - or .
    #max 63 per label

    return DomainSize and DomainChar and DomainFirst and DomainLast


def ValidIP(IP):

    try:
        result = ip_address(IP)
        return True
    except:         #ValueError Exception
        return False

def Answer2IP(Answer):
    answers = Answer.split(",") #potential multiple ips
    result = [] #<string>
    for a in answers: 
        #check IP addresses                                              
        if(ValidIP(a)):
            result.append(a)

    #print(result)
    return result

def ReadInLogs(LogList,clean=True):

    ReadinLogDict = dict() #MixIdentifier[id.orig_h+id.orig_p+id.resp_h+id.resp_p+trans_id]<String>:List<Strings>[Client,Domain,IPs]
    DomainDict = dict() #Domains<string>:appeared times<int> 
    ClientDict = dict() #Client<string>: appeared times<list<string>>
    IPDict = dict()     #IP<string>: Domain<string>
    RL = []#Record List Store a list of [DOmain,Client,IPs] for build other dictionary
    TotalLine = 0
    ValidLine = 0

    for Log in LogList:
        #print(Log)
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

                        RL.append([Domain,Client,IPList])
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

#Output three dict contain valid Client,Domain,IPs and their No.
#Domain Dict No<int>:Domain<String>
#Client Dict No<int>:Client<String> 
#IP Dict No<ing>: IP<String> 

def Prun(DomainDict,ClientDict,IPDict,TotalCall,kd=1,ka=1,kc=1): #defaulr settingska=0.25,kb=0.001,kc=3
    
    #make sure input isn't empty
    if(len(DomainDict) < 1 or len(ClientDict) < 1 or len(IPDict) < 1):
        return None

    MaxDomain = len(DomainDict)*kd #popular domain
    MaxClient = TotalCall*ka  #busy client 

    #print(MaxDomain," ",MaxClient)

    DomainNo = dict()
    ClientNo = dict()
    IPNo = dict()
    
    #Domain 
    index = 0 #may adjusted
    for domain in DomainDict:

        if(DomainDict.get(domain) < MaxDomain):
            DomainNo[index] = domain
            index += 1
    #Client
    index = 0
    for client in ClientDict:

        cNum = ClientDict.get(client)
        if(cNum < MaxClient and cNum >= kc):
            ClientNo[index] = client
            index += 1

    #IP
    index = 0
    for ip in IPDict:

        if(len(IPDict.get(ip)) > 1):
            IPNo[index] = ip
            index += 1

    #any of the empty dict should no reach here
    dp = (len(DomainNo)/len(DomainDict))*100
    cp = (len(ClientNo)/len(ClientDict))*100
    ipp = (len(IPNo)/len(IPDict))*100

    print("Pruned Data:\nDomain: {} ({:.3f}% remain)\nClient: {}({:.3f}% remain)\nIP: {}({:.3f}% remain)".format(len(DomainNo),dp,len(ClientNo),cp,len(IPNo),ipp))
    return (DomainNo,ClientNo,IPNo)


def GenerateWL(LogLists,kd=1,ka=1,kc=1,cleanFlag=True,prunFlag=True,ShowTime=True):
    
    st = datetime.now()
    RL,DD,CD,IPD,TCalls = ReadInLogs(LogLists,cleanFlag)
    et = datetime.now()
    tt = et - st
    print()
    if(ShowTime):print("Read in cost:{}".format(tt))
    #No empty dictionary
    if(len(DD) > 0 and len(CD) > 0 and len(IPD) > 0):
        print()
        print("Data {} Cleaned. Start pruning ... ".format(TCalls))
        if(prunFlag):
            
            st = datetime.now()
            Nos = Prun(DD,CD,IPD,TCalls,kd,ka,kc)
            et = datetime.now()
            tt = et - st
            print()
            if(ShowTime):print("Purn cost:{}".format(tt))
            return (RL,Nos)

    else:
        return None
    
def GenerateDomain2IP(RL,DD,IPD):
    
    Domain2IP = dict()
    Domains = list(DD.values())
    IPs = list(IPD.values())
    
    #intialization
    for dd in Domains:
        Domain2IP[dd] = []

    for record in RL:

        if(record[0] in Domain2IP): #valid domain
            for ip in record[2]:
                if(ip in IPs): Domain2IP[record[0]].append(ip)

    result = {key:list(set(val)) for key, val in Domain2IP.items() if len(val) > 0}
    return result





if "__name__" == "__main__":
    RL,TD = GenerateWL(["2021-02-09_dns.01:00:00-02:00:00.log"])#,kd=0.25,ka=0.001,kc=3)
    DD,CD,IPD = TD
    st = datetime.now()
    D2IP = GenerateDomain2IP(RL,DD,IPD)
    et = datetime.now()
    tt = et - st
    print("Time cost {}".format(tt))
    print("Dictionary size {}".format(len(D2IP)))
    #print(RL)
#for dip in D2IP:
#    print("{}: {}".format(dip,D2IP.get(dip)))
#for dd in DD:
#    print("[{}] {}".format(DD[dd],dd))
