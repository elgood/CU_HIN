from ipaddress import ip_address, ip_network
import ipaddress

ip_networks = {
    "10.2.1.0/23": "VoIP",
    "10.2.3.0/24": "VoIP",
    "10.4.0.0/16": "VoIP",
    "10.4.0.0/16": "VoIP",
    "10.5.0.0/16": "VoIP",
    "10.41.1.128/26" : "VPN",
    "10.180.0.0/16" : "VPN",
    "10.181.0.0/24" : "VPN",
    "10.181.1.0/24" : "VPN",
    "10.181.2.0/24" : "VPN",
    "10.181.3.0/24" : "VPN",
    "10.181.4.0/24" : "VPN",
    "10.181.5.0/24" : "VPN",
    "10.181.6.0/24" : "VPN",
    "10.181.7.0/24" : "VPN",
    "10.181.8.0/24" : "VPN",
    "10.181.10.0/24" : "VPN",
    "10.181.11.0/24" : "VPN",
    "10.181.12.0/24" : "VPN",
    "10.181.128.0/24" : "VPN",
    "10.181.129.0/24" : "VPN", 
    "10.181.128.0/24" : "VPN",   
    "10.181.130.0/24" : "VPN",
    "10.181.131.0/24" : "VPN",
    "10.181.132.0/24" : "VPN",
    "10.181.133.0/24" : "VPN",
    "10.181.134.0/24" : "VPN",
    "10.181.135.0/24" : "VPN",
    "10.181.136.0/24" : "VPN",
    "10.181.138.0/24" : "VPN",
    "10.181.139.0/24" : "VPN",
    "10.181.140.0/24" : "VPN",
    "10.184.0.0/24" : "VPN",
    "10.199.16.0/23" : "Wireless",
    "10.199.24.0/23" : "Wireless",
    "10.199.72.0/23" : "Wireless",
    "10.199.74.0/23" : "Wireless",
    "10.199.76.0/22" : "Wireless",
    "10.199.80.0/23" : "Wireless",
    "10.199.96.0/23" : "Wireless",
    "10.199.98.0/23" : "Wireless",
    "10.199.128.0/23" : "Wireless",
    "10.199.144.0/22" : "Wireless",
    "10.199.152.0/23" : "Wireless",
    "10.199.154.0/23" : "Wireless",
    "10.199.156.0/23" : "Wireless",
    "10.199.158.0/23" : "Wireless",
    "10.199.160.0/23" : "Wireless",
    "10.199.168.0/23" : "Wireless",
    "10.199.170.0/23" : "Wireless",
    "10.199.180.0/23" : "Wireless",
    "10.199.180.0/23" : "Wireless",
    "10.199.180.0/23" : "Wireless",
    "10.199.192.0/24" : "Wireless",
    "10.199.198.0/24" : "Wireless",
    "10.199.199.0/24" : "Wireless",
    "10.199.200.0/24" : "Wireless",
    "10.199.238.0/23" : "Wireless",
    "10.200.0.0/17" : "Wireless",
    "10.200.128.0/21" : "Wireless",
    "10.200.136.0/21" : "Wireless",   
    "10.200.144.0/20" : "Wireless",  
    "10.200.160.0/19" : "Wireless",
    "10.200.192.0/18" : "Wireless",
    "10.201.0.0/17" : "Wireless",
    "10.201.128.0/17" : "Wireless",
    "10.202.0.0/18" : "Wireless",
    "10.202.64.0/18" : "Wireless",
    "10.202.128.0/18" : "Wireless",
    "10.202.192.0/18" : "Wireless",
    "10.203.0.0/18" : "Wireless",
    "10.203.128.0/22" : "Wireless",
    "10.203.192.0/24" : "Wireless",
    "10.203.196.0/24" : "Wireless",
    "10.216.0.0/17" : "Wireless",
    "10.216.128.0/17" : "Wireless",
    "10.217.0.0/17" : "Wireless",
    "10.217.128.0/17" : "Wireless",
    "10.218.0.0/17" : "Wireless",
    "10.218.128.0/18" : "Wireless",
    "10.218.192.0/18" : "Wireless",
    "10.219.0.0/17" : "Wireless",
    "10.219.128.0/17" : "Wireless",
    "10.219.192.0/23" : "Wireless",
    "10.232.0.0/17" : "Wireless: EduRoam Campus Buildings", # This can be further broken down by Department
    "10.233.0.0/17" : "Wireless: EduRoam Campus Buildings", # This can be further broken down by Department
    "10.233.128.0/17" : "Wireless: EduRoam Residential Buildings", # This can be further broken down by Building
    "10.234.0.0/16" : "Wireless: EduRoam Residential Buildings", # This can be further broken down by Building
    "10.235.0.0/17" : "Wireless: EduRoam Residential Buildings", # This can be further broken down by Building
    "10.235.128.0/19" : "Wireless: EduRoam",
    "10.235.192.0/23" : "Wireless: EduRoam",
    "128.138.2.0/23" : "ResNet", # This can be further broken down by Building
    "128.138.4.0/22" : "ResNet", # This can be further broken down by Building
    "128.138.8.0/21" : "ResNet", # This can be further broken down by Building
    "128.138.16.0/21" : "ResNet", # This can be further broken down by Building
    "128.138.24.0/22" : "ResNet", # This can be further broken down by Building
    "128.138.30.0/23" : "ResNet", # This can be further broken down by Building
    "128.138.32.0/20" : "ResNet", # This can be further broken down by Building
    "128.138.49.0/26" : "Conference Rooms",
    "128.138.49.128/25" : "ResNet", # This can be further broken down by Building
    "128.138.50.0/23" : "ResNet", # This can be further broken down by Building
    "128.138.52.0/22" : "ResNet", # This can be further broken down by Building
    "128.138.56.0/22" : "ResNet", # This can be further broken down by Building
    "128.138.62.0/23" : "Admin",
    "128.138.96.0/19" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "128.138.128.0/18" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "128.138.192.0/19" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "128.138.224.0/21" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "128.138.232.0/22" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "128.138.236.0/23" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "128.138.238.0/24" : "Public Buildings, General Network Wired access (incl. Stadium)", # Can be broken down much further by geographic region/Department
    "172.21.73.0/24" : "Wired: Private", # Department/Organization/Building/Floor subnets. Can be broken down further, but becomes identifiable after this level
    "172.21.74.0/23" : "Wired: Private", # Department/Organization/Building/Floor subnets. Can be broken down further, but becomes identifiable after this level
    "172.21.76.0/22" : "Wired: Private", # Department/Organization/Building/Floor subnets. Can be broken down further, but becomes identifiable after this level
    "172.21.80.0/20" : "Wired: Private", # Department/Organization/Building/Floor subnets. Can be broken down further, but becomes identifiable after this level
    "172.21.96.0/19" : "Wired: Private", # Department/Organization/Building/Floor subnets. Can be broken down further, but becomes identifiable after this level
    "172.21.128.0/17" : "Wired: Private", # Department/Organization/Building/Floor subnets. Can be broken down further, but becomes identifiable after this level
}


def subnet_lookup(input_address):
    for network in ip_networks:
        if ipaddress.ip_address(input_address) in ipaddress.ip_network(network, strict=False):
            return str(input_address) + ' is on subnet ' + str(network) + '|' + str(ip_networks[network]) + '\n'


