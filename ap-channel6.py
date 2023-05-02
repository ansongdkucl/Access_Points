from netmiko import ConnectHandler
import re
import os
import time

# define device parameters
pattern = r"-\d+$"

username = os.environ.get('username')
password = os.environ.get('password')
secret = os.environ.get('secret')


device = {
    'device_type': 'cisco_ios',
    'ip': '172.17.57.240',
    'username': username,
    'password': password,
    'secret': secret
}

# connect to device
net_connect = ConnectHandler(**device)

# initialize ap_num
ap_num = 100

# retrieve LLDP neighbors
# initialize dictionary to keep track of port channel numbers
ap_dict = {}

# retrieve LLDP neighbors
net_connect.enable()
lldp_output = net_connect.send_command('show lldp neighbors')

# parse LLDP output to extract APs
ap_list = []
lldp_lines = lldp_output.splitlines()

for line in lldp_lines:
    if 'AP' in line:
        # try to extract the AP name and interface from the line
        try:
            ap_name = line.split()[-5]
            ap_int = line.split()[-4]
        except IndexError:
            print(f"Skipping malformed LLDP line: {line}")
            continue
        
        # check if we have already assigned a port channel number to this AP name
        if ap_name in ap_dict:
            ap_num = ap_dict[ap_name]
        else:
            # assign a new port channel number to this AP name
            ap_num = len(ap_dict) + 100
            ap_dict[ap_name] = ap_num
        
        ap_list.append({'name': ap_name, 'ap_num': ap_num, 'channel': None, 'int': ap_int})

# create a set to keep track of port channels that have already been configured
configured_channels = set()

# configure port channels on device
for ap in ap_list:

            # create the port channel for the AP
            print(f'Configuring port channel po{ap["ap_num"]} for AP {ap["name"]}')
            config_commands = [
                f'interface po{ap["ap_num"]}',
                f'des  {ap["name"]}',
                'switchport access vlan 990',
                'switchport mode access'
            ]
            
            config_output = net_connect.send_config_set(config_commands)
            print(config_output)
            print(f'Configured port channel po{ap["ap_num"]} for AP {ap["name"]}')

            # add the port channel to the set of configured channels
            configured_channels.add(ap["ap_num"])



            config_commands1 = [
                f'default interface {ap["int"]}',
                f'interface {ap["int"]}',
                f'switchport access vlan 990',
                f'switchport mode access'
                ,f'channel-group {ap["ap_num"]} mode active'
                ,# configure port channels on device
                
            ]
            
            
            config_commands2 = [
                f'default interface {ap["int"]}',
                f'interface {ap["int"]}',
                f'switchport access vlan 990',
                f'switchport mode access'
                ,
                
            ]
            print('/n/n')
            config_output = net_connect.send_config_set(config_commands1)
            print(config_output)
            time.sleep(2)  # wait for 2 seconds before sending the next set of configuration commands

