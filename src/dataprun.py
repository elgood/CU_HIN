import re
from datetime import datetime
from ipaddress import ip_address 

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

    ReadinLogList = [] #Lists of inputed data
    DomainDict = dict() #Domains<string>:appeared times<int> 
    ClientDict = dict() #Client<string>: appeared times<list<string>>
    IPDict = dict()     #IP<string>: Domain<string>

    for Log in LogList:
        #print(Log)
        try:
            with open(Log,"r") as LogData:

                Data = LogData.readlines()
                print("Inputing {} logs ... ".format(len(Data)))
                for line in Data:
                    AddFalse = False

                    if(line[0] != "#"): #later use re
                        DataList = line.strip().split("\t") #if not fit to the given format, program stoped
                        IPList = Answer2IP(DataList[21])
                        if((ValidDomain(DataList[9]) and len(IPList) > 1)or not clean):
                            #print("{} -->  {}".format(DataList[9],DataList[21]))
                            ReadinLogList.append(DataList)

                            for ip in IPList:
                                
                                if(IPDict.get(ip) == None): #Domain not exist
                                    IPDict[ip] = [DataList[9]] #add domain
                                else:
                                    IPDict[ip].append(DataList[9])

                            if(DomainDict.get(DataList[9]) == None): #Domain not exist
                                DomainDict[DataList[9]] = 1 #appear once
                            else:
                                DomainDict[DataList[9]] += 1

                            if(ClientDict.get(DataList[2]) == None): #Domain not exist
                                ClientDict[DataList[2]] = [DataList[9]] #add domain
                            else:
                                ClientDict[DataList[2]].append(DataList[9])
                            
                            iplist = Answer2IP(DataList[21])


                            if(len(iplist) == 0): #no valid ip addresses
                                AddFlag = False
                            for ip in iplist:
                                
                                if(IPDict.get(ip) == None): #Domain not exist
                                    IPDict[ip] = [DataList[9]] #add domain
                                else:
                                    IPDict[ip].append(DataList[9])

                #ip dns
        except:
            print("ERROR: INVALID FILE ADDRESS OR NAME")


    #print(len(ReadinLogList))
    return (ReadinLogList,DomainDict,ClientDict,IPDict)

def Prun(LogsList,DomainDict,ClientDict,IPDict,kd=1,ka=1,kc=1): #defaulr settingska=0.25,kb=0.001,kc=3
    
    MaxDomain = len(DomainDict)*kd #popular domain
    MaxClient = len(LogsList)*ka   #bust client 

    ClientNumCallDict = dict() #<string>:(<int>,<int>)
    for c in ClientDict:

        ClientList = ClientDict.get(c) #should not failed
        ClientNumCallDict[c] = (len(ClientList),len(set(ClientList)))

    resultList = []
    for log in LogsList:

        DomainNum = DomainDict.get(log[9]) #should not failed
        Clientdata =  ClientNumCallDict.get(log[2])
        ClientNum = Clientdata[0]
        ClientCall = Clientdata[1]

        #print("Client {}: call {} domain {} ; Domain {}: {}".format(log[2],ClientNum,ClientCall,log[9],DomainNum))

        if(DomainNum <= MaxDomain and ClientNum <= MaxClient and ClientCall >= kc):
            resultList.append(log)


    return resultList


def LogDataProcess(LogLists,kd=1,ka=1,kc=1,cleanFlag=True,prunFlag=True,ShowTime=True):
    
    st = datetime.now()
    CL,DD,CD,IPD = ReadInLogs(LogLists,cleanFlag)
    et = datetime.now()
    tt = et - st
    if(ShowTime):print("Read in cost:{}".format(tt))
    if(len(CL) != 0):
        print("Cleaned Data {} ".format(len(CL)))
        if(prunFlag):
            
            st = datetime.now()
            RL = Prun(CL,DD,CD,IPD,kd,ka,kc)
            et = datetime.now()
            tt = et - st
            if(ShowTime):print("Purn cost:{}".format(tt))
            print()
            precent = 100*(len(RL)/len(CL))
            print("Pruned Data:{} {}% of cleaned data".format(len(RL),precent))
            CL = RL
            print()
    #else: errors
    print("{} Clients \n{} Domains \n{} IPs\n".format(len(CD),len(DD),len(IPD)))
    return (CL,DD,CD,IPD)
    



if "__name__" == "__main__":
    CL,DD,CD,IPD = LogDataProcess(["2021-02-12_dns.04:00:00-05:00:00.log"])

