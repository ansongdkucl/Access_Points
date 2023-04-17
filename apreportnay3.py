import napalm
import csv
from napalm import get_network_driver
import os

# Define the device and credentials
device_ip = ['172.18.1.1','172.18.1.2','172.18.1.10','172.18.1.11','172.18.1.12','172.18.1.13','172.18.1.20','172.18.1.21'
             ,'172.18.1.22','172.18.1.30','172.18.1.31','172.18.1.32','172.18.1.40','172.18.1.41','172.18.1.42','172.18.1.50'
             ,'172.18.1.51','172.18.1.52','172.18.1.60','172.18.1.61','172.18.1.62','172.18.1.70','172.18.1.71','172.18.1.72'
             ,'172.18.1.80','172.18.1.81']

username = os.environ.get('username')
password = os.environ.get('password')
secret = os.environ.get('secret')

# Initialize the list to store the LLDP information
lldp_info = []

for ip in device_ip:
    # Connect to the device
    driver = get_network_driver('ios')
    device = driver(ip, username, password, optional_args={'secret': secret})
    device.open()

    # Get the hostname
    facts = device.get_facts()
    hostname = facts['hostname']

    # Retrieve the LLDP information
    lldp = device.get_lldp_neighbors_detail()

    # Retrieve the interfaces and their IP addresses
    interfaces_ip = device.get_interfaces_ip()

    # Filter the LLDP information based on the remote system name
    filtered_lldp = []
    for interface, neighbors in lldp.items():
        for neighbor in neighbors:
            if 'AP' in neighbor.get('remote_system_name', ''):
                # Get the VLAN ID from the interface name
                vlan_id = interface.split('.')[1] if '.' in interface else ''
                # Get the IP address of the local interface
                local_ip = next(iter(interfaces_ip.get(interface, {}).values()), '')
                filtered_lldp.append((hostname, interface, vlan_id, neighbor.get('remote_system_name', ''), neighbor.get('remote_chassis_id', ''), neighbor.get('remote_port', ''), neighbor.get('remote_port_description', ''), neighbor.get('remote_system_description', ''), local_ip))

    # Add the filtered LLDP information to the list
    lldp_info += filtered_lldp

    # Close the connection to the device
    device.close()

# Sort the LLDP information by the report port field
lldp_info_sorted = sorted(lldp_info, key=lambda x: x[4])

# Print the output to the screen
for neighbor in lldp_info_sorted:
    print(f'{neighbor[0]} {neighbor[1]} {neighbor[2]} {neighbor[3]} {neighbor[4]} {neighbor[5]} {neighbor[6]} {neighbor[7]} {neighbor[8]}')

# Write the output to a CSV file
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Hostname', 'Local Interface', 'VLAN ID', 'Remote System Name', 'Remote Chassis ID', 'Remote Port', 'Remote Port Description', 'Remote System Description', 'Local IP'])
    for neighbor in lldp_info_sorted:
        writer.writerow([neighbor[0], neighbor[1], neighbor[2], neighbor[3], neighbor[4], neighbor[5], neighbor[6], neighbor[7], neighbor[8]])