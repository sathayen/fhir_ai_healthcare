import requests
import json
import os
from dotenv import load_dotenv
load_dotenv(override=True)

fhir_resource = os.environ['AZURE_FHIR_ENDPOINT']
fhir_client_id = os.environ['AZURE_FHIR_CLIENT_ID']
fhir_client_secret = os.environ['AZURE_FHIR_CLIENT_SECRET']
fpc_cookie = os.environ['FPC_COOKIE']

def get_fhir_access_token():
    url = "https://login.microsoftonline.com/353d521a-56bd-4062-acb6-1c90a53d350e/oauth2/token"

    payload = 'grant_type=Client_Credentials&resource={}&client_id={}&client_secret={}'.format(fhir_resource, 
                                                                                               fhir_client_id, 
                                                                                               fhir_client_secret)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'fpc={}; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd'.format(fpc_cookie)
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    res = json.loads(response.text)

    return res['access_token']

if __name__ == '__main__':
    token = get_fhir_access_token()
    print(token)