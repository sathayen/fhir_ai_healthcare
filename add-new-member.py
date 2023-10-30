import os
from dotenv import load_dotenv
import json
from get_fhir_token import get_fhir_access_token
from create_fhir_records import create_coverage_record
from create_fhir_records import create_patient_record
from create_fhir_records import create_related_person_record
from get_fhir_records import get_fhir_patient_record

# Load environment variables
load_dotenv()

# Replace with your Azure FHIR API endpoint and authentication token
azure_fhir_endpoint = os.environ["AZURE_FHIR_ENDPOINT"]
#azure_fhir_auth_token = os.environ["AZURE_FHIR_AUTH_TOKEN"]
azure_fhir_auth_token = get_fhir_access_token()

# Define the FHIR resource endpoint for coverages
resource_endpoint = f"{azure_fhir_endpoint}/Coverage"

def add_dependent(dependent_info_dict, parent_patient_id):
    # First validate the main subscriber (parent patient)
    response = get_fhir_patient_record(parent_patient_id)
    print("status_code:", response.status_code)
    
    # Validate if the record exists
    if response.status_code != 201:
        print("No patient record found")
        print("TODO: communicate with the caller/ agent of the missing record, human intervention needed")
        #raise RecordNotFoundException
        return
    
    # The record has been validated, it is OK to proceed now. 
    print("TODO: add a sanity checker for the dependent info dict")
    
    # Create a new "relatedPerson record"
    response = create_related_person_record(payload=dependent_info_dict["related_person"])
    
    # Create a new Coverage record for this related person
    response = create_coverage_record(payload=dependent_info_dict["coverage"])

def test_create_dummy_patient_and_coverage():
    pass


if __name__ == "__main__":
    
    # create a dummy patient for testing.
    patient_payload= {
        "gender": "female",
        "birthdate": "1970-01-15",
        "family_name": "Smith1970",
        "official_given_names": ["ChellyBella"],
        "usual_given_names" : ["Chelly"]
    }

    response = create_patient_record(payload=patient_payload)
    print("-"*80)
    print("type response:", type(response.text))
    response_json = json.loads(response.text)
    print(response_json)
    print("type response_json=", type(response_json))
    # Sample payload containing values to update
    parent_patient_id = response_json["id"]
    print("patent patient id =", parent_patient_id)
    print("-"*80)
    print("parent record =", response.text)
    print("-"*80)
    
    # Create dummy coverage for this parent patient
    # payload = {
    #     "id": "9876C1", #this is coverage id, actually it will be automatically created
    #     "beneficiary": {
    #         "reference": "Patient/{}".format(parent_patient_id)
    #     },
    #     "dependent": "0",
    #     "dependent_code": "self" # other options in FHIR R4 self, spouse, child, other 
    # }
    coverage_data = {
        "id": "9876C1", #this is coverage id, actually it will be automatically created
        "beneficiary": {
            "reference": "Patient/{}".format(parent_patient_id)
            },
        "subscriber": {
            "reference": "Patient/{}".format(parent_patient_id)
            },
    }
    
    # response = create_coverage_record(coverage_data)
    
    # dependent_info_dict = {
    #     "related_person": {
    #         "gender": "male",
    #         "birthdate": "2001-01-15",
    #         "family_name": "Smith1970",
    #         "given_names": ["John"],
    #         "reference": "Patient/{}".format(parent_patient_id), #parent patient reference id
    #         "code": "SON",
    #         "display": "Son"
    #     },
    #     "coverage": {
    #         "id": "9876C1", #coverage id, this wil not be needed, it should be autro generated
    #         "beneficiary": {
    #             "reference": "Patient/new-beneficiary-id"
    #         },
    #         "dependent": "1",
    #         "dependent_code": "child" # other options in FHIR R4 self, spouse, child, other 
    #     }
    # }
    
    # add_dependent(dependent_info_dict=dependent_info_dict, 
    #               parent_patient_id=parent_patient_id)
    