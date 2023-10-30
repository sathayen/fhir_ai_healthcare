import os
import requests
from get_fhir_token import get_fhir_access_token

from dotenv import load_dotenv
load_dotenv()

fhir_endpoint = os.environ['AZURE_FHIR_ENDPOINT']
fhir_samples_dir = os.environ['FHIR_SAMPLES_DIR']

def _get_record(record_id, resource_type):
    url = "{}/{}/{}".format(fhir_endpoint, resource_type, record_id)
    payload = {}
    access_token = get_fhir_access_token()
    headers = { 'Authorization': 'Bearer {}'.format(access_token) }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def get_fhir_patient_record(patient_id):
    return _get_record(record_id=patient_id, resource_type="Patient")
    