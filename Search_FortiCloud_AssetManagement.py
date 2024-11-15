import requests

# APIv3
# THIS SCRIPT SEARCHES FOR A FORTIGATE SERIAL NUMBER BASED ON DESCRIPTION TEXT.

# URLS
AUTH_URL = "https://customerapiauth.fortinet.com/api/v1/oauth/token/"
BASE_URL = "https://support.fortinet.com/ES/api/registration/v3"

# Credentials | # Ensure the account has read access to assetmanagement. Nothing more is needed for the purpose of this script
api_key = ''
passwd = ''


# Default
headers = {
    'Content-Type': 'application/json',
    }


def get_access_token():
    auth_payload = {
        "username": api_key,
        "password": passwd,
        "client_id": "assetmanagement",
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
            "serialNumber": "FGT"
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
        print(f'''\nNo Results found. This script will search for a device exactly as you enter it unless you include " --contain"\nTry "{actual_device} --contain" or enter exactly as its named in asset management.''')
        return None
    else:
        for devices in results:
            print(f"{i}. {devices}")
            option = str(i), devices
            options.append(option)
            i += 1

        select = input("\nSelect the device you would like to provision.: ")
        for option in options:
            if select == option[0]:
                print(f"\nYou have selected {option[1]}.")
                serialNumber_selected = option[1][0]
                return serialNumber_selected
            
        

def main():

    # Lists
    inventory = list()
    results = list()
    options = list()

    device_request = input("Search Device Name: ")
    access_token = get_access_token()
    assets = get_devices(access_token)

    # place results in a list to later search by device name (description)
    for resource in assets:
        device = resource["serialNumber"], resource["description"]
        inventory.append(device)


    serialNumber_selected = show_menu(results, inventory, device_request, options)

    # code what youd like to do with the serial retrieved
    print(f"Retrieved: {serialNumber_selected}")


if __name__ == "__main__":
    main()