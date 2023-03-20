from nornir import InitNornir
import re
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_netmiko.tasks import netmiko_send_config
from nornir.core.inventory import Group
import time
import pysnmp
import smtplib
import datetime
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from nornir.core.filter import F
import requests
import json


# Email variables
fromaddr = "d.ansong@ucl.ac.uk"
toaddr = "d.ansong@ucl.ac.uk"
#server = smtplib.SMTP('smtp-server.ucl.ac.uk', 587)
#server = smtplib.SMTP('144.82.253.10', 587)

interfaces = []
#venMAC = ['000b.']
#venMAC = ['0090.8f']
venMAC = ['000b.8','0090.8f']

def find(task):

    for mac_add in venMAC:
        #print('mac search')
       # r = task.run(netmiko_send_command, command_string="show mac add | inc {}".format(venMAC),enable=True)
        r = task.run(netmiko_send_command, command_string="show mac add | inc 000b.8",enable=True)
        content = r.result
        #print(content)

        if mac_add in content:  
            int_pat = re.findall(r'Te\d\/\d+\/\d+|Gi\d\/0\/\d+|fa0\/\d+',content)
            mac_pat = re.findall(r'([0-9a-z]{4}[\.][0-9a-z]{4}[\.][0-9a-z]{4})',content)
            #Remove duplicates from list 'pat' and create new list 'interfaces
            interfaces = list(set(int_pat))
            #print('Devices Found on {} on {}'.format(task.host,interfaces))     
            
            for dev in interfaces:#
                r1 = task.run(netmiko_send_command, command_string="show int status | inc {}".format(dev),enable=True)        
                #print(r1.result)

                if 'trunk' in r1.result:
                    break
                   # print("port is trunk no action taken")
    
                else:
                    #print(dev)                   
                    r2 = task.run(netmiko_send_command, command_string="show run int {} | inc 990".format(dev),enable=True)

                    r_snmp = task.run(netmiko_send_command, command_string="show snmp location", enable=True)
                    snmp = r_snmp.result.strip()
                   

                    sw_string = r2.result.lstrip()
                    print(sw_string)   
                    
                 
                    string_1 = 'switchport access vlan 990'
             
                 
            
                    if string_1 in sw_string :
                        print(dev,'device already on vlan 990')
                        #break
                      
                    else:
                        print('change vlan on',task.host,dev)
                        r4 = task.run(netmiko_send_command, command_string="show mac address-table int {}".format(dev),enable=True)
                        content = r4.result
                        mac_pat1 = re.findall(r'([0-9a-z]{4}[\.][0-9a-z]{4}[\.][0-9a-z]{4})',content)
                        mac_pat2 = list(set(mac_pat1))
                        #print(mac_pat2)


                        r3 = task.run(netmiko_send_config, config_commands=["int {}".format(dev),"switchport access vlan {}".format('990')])
                        print(r3)

                        r3 = task.run(netmiko_send_config, config_commands=['show run int gi1/0/33 | inc 990'])
                        print(r4.result)
                        
                        
                     
                        print(f'Switch {task.host} (no Location found) port {dev} mac - {mac_pat2} on Vlan 990')
                    
                        #Sends webhook to my Teams Channel                        
                    
                        url = 'https://liveuclac.webhook.office.com/webhookb2/d6a331ab-271a-4b6d-9731-36c1f97f2bde@1faf88fe-a998-4c5b-93c9-210a11d9a5c2/IncomingWebhook/e008a9eb7e5b4b8daab1307a1090014c/43bfe760-7689-4d0b-96fd-46b265519580'
                        message = {
                            'text': f'The following device has been configured below:\\\n AP MAC - {mac_pat2} \\\nSwitch {task.host} - Port {dev} - Vlan 990 - {snmp}'
                        }
                        response_body = requests.post(url=url,data=json.dumps(message))


#nr = InitNornir(config_file='/home/ansongdk/projects/nornir-projects/auto-vlan/config.yaml')
nr = InitNornir(config_file='/home/ansongdk/scripts/config.yaml')
#voip = nr.filter(F(groups__contains="cisco-ioe"))
result = nr.run(name='find mac address',task=find)


 #131    000b.86a0.7747    STATIC      Gi1/0/33























#result = voip.run(name='find mac address',task=find)
#Team id = #"id": "d6a331ab-271a-4b6d-9731-36c1f97f2bde",
#Channel id #"id": "d6a331ab-271a-4b6d-9731-36c1f97f2bde",
#"id": "d6a331ab-271a-4b6d-9731-36c1f97f2bde",
# client secret 2733a15f-de2e-4c93-8caa-98adc0a9b5d4
# client id f7f1be95-ff88-4ecf-b239-f236ec63d28a
# tennent id 1faf88fe-a998-4c5b-93c9-210a11d9a5c2
# "driveId": "b!PgdE6gYKnkaW4ii2JWL_8Bxp_749m61LjQKHtiM6TMv7c9XMXI8IS4ZSpdlWk9Q8",
#file id 12258edd-4a39-483d-b713-b17c7b862848
#https://liveuclac.sharepoint.com/:x:/r/sites/WiFiAutomatedRollOut/Shared%20Documents/School%20of%20Pharmacy/sopwifi.xlsx?d=w12258edd4a39483db713b17c7b862848&csf=1&web=1&e=nqcEA9
# https://liveuclac.sharepoint.com/:x:/r/sites/WiFiAutomatedRollOut/_layouts/15/Doc.aspx?sourcedoc=%7B12258EDD-4A39-483D-B713-B17C7B862848%7D&file=sopwifi.xlsx&action=default&mobileredirect=true
#https://graph.microsoft.com/v1.0/teams/d6a331ab-271a-4b6d-9731-36c1f97f2bde/channels
#https://graph.microsoft.com/v1.0/teams/d6a331ab-271a-4b6d-9731-36c1f97f2bde/channels/19:a762edac34764391b459640ab7866ee2@thread.tacv2/filesFolder\ 

#https://graph.microsoft.com/v1.0/teams/{team-id}/channels/{channel-id}/files
#https://graph.microsoft.com/v1.0/teams/d6a331ab-271a-4b6d-9731-36c1f97f2bde/channels/19:a762edac34764391b459640ab7866ee2@thread.tacv2/filesFolder

#https://graph.microsoft.com/v1.0/drives/{drive-id}/items/{item-id}
#https://graph.microsoft.com/v1.0/drives/b!PgdE6gYKnkaW4ii2JWL_8Bxp_749m61LjQKHtiM6TMv7c9XMXI8IS4ZSpdlWk9Q8/items/12258edd-4a39-483d-b713-b17c7b862848



