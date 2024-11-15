import requests
import os, time, sys


# Based on version 1.0 FortiZTP API Documentation


# URLS | ZTP & Assem Management
AUTH_URL = "https://customerapiauth.fortinet.com/api/v1/oauth/token/"

BASE_URL = "https://support.fortinet.com/ES/api/registration/v3" # AssetManagement
BASE_ZTP_URL = "https://fortiztp.forticloud.com/public/api/v1/devices/" # FortiZTP
# path urls are contained within function

# Credentials
api_key = ''
passwd = ''

# Remote Public FortiManager Information (NOT for FortiGate Cloud or FortiManager Cloud)
fmg_sn = ''
fmg_ip = '' # Public IP

# Will need to be changed if provisioning a different appliance on the FortiZTP portal
# other options - FortiAP, FortiSwitch and FortiExtender
device_type = 'FortiGate'

appliance = "FGT" # FortiGate 60 series # First 3 characters of the products serial number
# If you would like to include more appliances, you can create a list and include all appliances. 
# You will need to adjust the rest of the script 

# Default
headers = {
    'Content-Type': 'application/json',
    }

# Useful functions 
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')



# Core functions
def get_access_token(client):
    print(f"Authenticating to {client} platform...")
    auth_payload = {
        "username": api_key,
        "password": passwd,
        "client_id": client,
        "grant_type": "password",
        }
    

    try:
        r = requests.post(AUTH_URL, headers=headers, json=auth_payload)
        print(f"Authentication Status Code: ", r.status_code)
        r = r.json()
        access_token = r["access_token"]
        return access_token
    
    except Exception as error:
        print(f"Access Token Error: {error}")
        return None
    

def get_devices(access_token):
    try:
        path = '/products/list'
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {access_token}"
        }

        data_request = {
            "serialNumber": appliance
        }

        r = requests.post(BASE_URL+path, headers=headers, json=data_request)
        print(f"Resource Call Status Code: {r.status_code}\n")
        assets = r.json()
        assets = assets["assets"]
        return assets
    
    except Exception as error:
        print(f"Error occurred: {error}")

def show_menu(results, inventory, device_request, options):
    i = 0
    actual_device = device_request.strip(" --contain")

    for device in inventory:
        if device_request.find(" --contain") > -1:
            if actual_device in device[1]:  #description
                results.append(device)
        elif device_request.find(" --contain") <= -1:
            if actual_device == device[1]:  #description
                results.append(device)
           
    if len(results) == 0:
        print(f'''\nNo Results found. This script will search for a device exactly as you enter it unless you include " --contain"\nTry "{actual_device} --contain" or enter exactly as its named in asset management.\n\n''')
        return None
    else:
        for devices in results:
            print(f"{i}. {devices}")
            option = str(i), devices
            options.append(option)
            i += 1

        select = input("\nSelect an option to interact with: ")
        for option in options:
            if select == option[0]:
                print(f"\nYou have selected {option[1][0]} - {option[1][1]}.\n")
                SN = option[1][0]
                return SN
            else:
                print("None selected.")
                return None


# # # ZTP # # #
def get_device(access_token, SN):
    print("Retrieving ZTP assets...")
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {access_token}"
    }
    try:
        r = requests.get(BASE_ZTP_URL+SN, headers=headers)
        jsonresponse = r.json()

        ztp_provision_status = jsonresponse["provisionStatus"]
        device_sn = jsonresponse["deviceSN"]
        target = jsonresponse["externalControllerIp"]
        print(f"\nFortiGate Serial Number: {device_sn}")
        print(f"Provision Status: {ztp_provision_status}")
        print(f"Provision Target: {target}")

        # returning status for validation portion only
        return ztp_provision_status
    
    except Exception as error:
        print(f"Retrieval of Device Error: {error}")

    return None

def provision_device(access_token, SN):
    print("Provisioning device....")
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {access_token}"
        }
    provision_data = {
        # FortiGate
        "deviceSN": SN,
        "deviceType": device_type,
        "provisionStatus": "provisioned",
        "provisionTarget": "FortiManager",
        # FortiManager
        "externalControllerSn": fmg_sn,
        "externalControllerIp": fmg_ip,
    }

    try:
        r = requests.put(BASE_ZTP_URL+SN, headers=headers, json=provision_data)
        print(f"Status Code: ", r.status_code)
        print(r.json())

        
    
    except Exception as error:
        print(f"Provision Device Error: {error}")

def deprovision_device(access_token, SN):
    print("Deprvisioning device....")
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {access_token}"
        }
    provision_data = {
        # FortiGate
        "deviceSN": SN,
        "deviceType": device_type,
        "provisionStatus": "unprovisioned",
        "provisionTarget": "FortiManager",
        # FortiManager
        "externalControllerSn": fmg_sn,
        "externalControllerIp": fmg_ip,
    }
    try:
        r = requests.put(BASE_ZTP_URL+SN, headers=headers, json=provision_data)
        print(f"Status Code: ", r.status_code)
        print(r.json())
    
    except Exception as error:
        print(f"Provision Device Error: {error}")




def main():

    # Lists
    inventory = list()
    results = list()
    options = list()


    device_request = input("Enter device name (desc) or Serial #: ")

    if device_request.startswith(appliance): 
        SN = device_request
    else:
        client = "assetmanagement"
        access_token = get_access_token(client)
        assets = get_devices(access_token)

        # place results in a list to later search by device name (description)
        for resource in assets:
            device = resource["serialNumber"], resource["description"]
            inventory.append(device)


        SN = show_menu(results, inventory, device_request, options)
        if SN is None:
            main()


    # Switch to FortiZTP Portal 
    client = "fortiztp"
    access_token = get_access_token(client)
    get_device(access_token, SN)
    ans = input('''
    1. Provision
    2. Deprovision
                
    Press any other key to cancel...\n
    ''')
    if ans == '1':
        provision_device(access_token, SN)
        print("Provisioning...")

        time.sleep(1)

        print("Pulling provisioning status...") # Initial check for provision status
        dev_status = get_device(access_token, SN)

        while dev_status != 'provisioned':
            print(f"Current Device Status: {dev_status}. Checking every 5 seconds.")
            print("Waiting for provision status to update.")
            time.sleep(5)
            
            dev_status = get_device(access_token, SN)

            if dev_status == "waiting" or dev_status == "provisioning":
                print(f"Current Device Status: {dev_status}. Running some backend processes..")
                time.sleep(5)

            if dev_status == "provisioningtoolong":
                print(f"Current Device Status: {dev_status}.")
                print("The device took too long. It may be offline or is unable to reach the internet.")
                print("Ensure the device is powered or try rebooting.")
                time.sleep(5)
        
    elif ans == '2':
        deprovision_device(access_token, SN)
    else:
        print("Script has left the chat.")
        sys.exit(0)




if __name__ == "__main__":
    main()

