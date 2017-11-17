#!/usr/bin/env python

"Use the Managed Service Identity service in Azure to get an auth token"

import os
import sys
import requests
import json
import subprocess
import azhadbg
from pathlib import Path

# Specify files accessed by this script
get_response_file = "/home/guestshell/azure/token_get_rsp"
token_file = "/bootflash/token"
at_file = "/home/guestshell/azure/at_command_file"
debug_file = "/home/guestshell/azure/azhadbg.log"
msi_dir = "/var/log/azure/Microsoft.ManagedIdentity.ManagedIdentityExtensionForLinux"

# Check if user has successfully installed the Managed Identity Extension
if not os.path.exists(msi_dir):
    # Directory does not exist.  Don't use MSI
    os.system('sudo rm /bootflash/token')
    sys.exit()

# Open the debug log file
debug_fh = open(debug_file, 'a')
azhadbg.log(debug_fh, "Requesting new token")

# Specify the HTTP GET request to obtain a token
url      = "http://localhost:50342/oauth2/token"
payload  = {'resource':'https://management.azure.com/'}
header   = {'Metadata':'true'}

# Send the HTTP GET request for the token
response = requests.get(url, params=payload, verify=False, headers=header)

if 200 == response.status_code :
    # Write the HTTP GET response to a file for debugging purposes
    with open(get_response_file, 'wb') as resp_fh:
        for chunk in response.iter_content(chunk_size=64):
            resp_fh.write(chunk)
    azhadbg.log(debug_fh, "Token obtained successfully")
else:
    azhadbg.log(debug_fh, "Token GET request failed with code %d" % response.status_code)
    debug_fh.close
    sys.exit

# Parse the HTTP GET response
token = response.json()["access_token"]

# Write the token to the token file
with open(token_file, 'w') as token_fh:
    token_fh.write(token)

# Calculate the period of time this token is valid
expires_in = response.json()["expires_in"]
azhadbg.log(debug_fh, "Token expires in %d seconds" % int(expires_in))
exp_minutes = (int(expires_in) / 60) - 5
azhadbg.log(debug_fh, "Token will be refreshed in %d minutes" % exp_minutes)

# Schedule a job to invalidate this token
#command = "/usr/bin/at -f at_file now + %d minutes" % exp_minutes
#os.system(command)

debug_fh.close


