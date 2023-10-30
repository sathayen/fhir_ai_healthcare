import requests
import json
import jsonpatch
from get_fhir_token import get_fhir_access_token
import os
from dotenv import load_dotenv
load_dotenv(override=True)
fhir_endpoint = os.environ['AZURE_FHIR_ENDPOINT']
fhir_samples_dir = os.environ['FHIR_SAMPLES_DIR']

def _create_record(payload, resource_type):
    url = "{}/{}".format(fhir_endpoint, resource_type)
    
    access_token = get_fhir_access_token()
    
    headers = {
        'x-ms-profile-validation': 'true',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(access_token)
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("Response status code:", response.status_code)
    print("-"*80)
    print(response.text)
    return response
    
def update_patient_info(patient_data, payload):
    # Example data
    # patient_data = {
    #     "gender": "female",
    #     "birthdate": "1970-01-15",
    #     "family_name": "Smith1970",
    #     "official_given_names": ["ChellyBella"],
    #     "usual_given_name" : ["Chelly"]
    # }
    try:
        gender = payload["gender"]
        birthdate = payload["birthdate"] 
        family_name = payload["family_name"]
        official_given_names = payload["official_given_names"] 
        usual_given_names = payload["usual_given_names"]

        # Create a list of JSON Patch operations
        patch_operations = [
            {"op": "replace", "path": "/gender", "value": gender},
            {"op": "replace", "path": "/birthDate", "value": birthdate},
            
            
        ]

        # Find the index of the "official" and "usual" name objects
        official_index = None
        usual_index = None
        
        print("debug patient data: ", patient_data)
        print("debug type(patient_data) : ", type(patient_data))
        print("debug: patient_data['name'] = ", patient_data['name'])
        print("debug: type(patient_data['name'])", type(patient_data['name']))

        if "name" in patient_data and isinstance(patient_data["name"], list):
            for i, name in enumerate(patient_data["name"]):
                if "use" in name and name["use"] == "official":
                    official_index = i
                elif "use" in name and name["use"] == "usual":
                    usual_index = i

        # Update the given names based on the "use" field
        if official_index is not None:
            patch_operations.append({"op": "replace", 
                                     "path": f"/name/{official_index}/given", 
                                     "value": official_given_names})
            patch_operations.append({"op": "replace", 
                                     "path": f"/name/{official_index}/family", 
                                     "value": family_name})

        if usual_index is not None:
            patch_operations.append({"op": "replace", 
                                     "path": f"/name/{usual_index}/given", 
                                     "value": usual_given_names})
          
        # Apply the JSON Patch to update the fields
        patched_data = jsonpatch.apply_patch(patient_data, patch_operations)

        # Convert the modified data back to JSON
        modified_json = json.dumps(patched_data, indent=4)
        return modified_json

    except json.JSONDecodeError as e:
        return f"Error: {str(e)}"


def create_patient_record(payload={}):
    file_path = os.path.join(fhir_samples_dir, "patient.json")
    with open(file_path) as f:
        #temp = json.load(f)
        #data_template = json.dumps(temp)
        data_template = json.load(f)
        
        if not payload:
            record_payload = data_template
        else:
            # TODO: Check for errors
            record_payload = update_patient_info(data_template, payload)
            
    return _create_record(record_payload, resource_type="Patient")

    
def create_related_person_record(payload={}):
    file_path = os.path.join(fhir_samples_dir, "relatedPerson.json")
    with open(file_path) as f:
        temp = json.load(f)
        data_template = json.dumps(temp)
        
        if not payload:
            record_payload = data_template
        else:
            # TODO: Check for errors
            record_payload = update_related_person_info(data_template, payload)
    
    return _create_record(record_payload, resource_type="RelatedPerson")
     
def update_related_person_info(related_person_data, payload):
    try:
        gender = payload["gender"]
        birthdate = payload["birthdate"]
        family_name = payload["family_name"]
        given_names = payload["given_names"]
        reference = payload["reference"]
        code = payload["code"]
        display = payload["display"]

        # Create a list of JSON Patch operations
        patch_operations = [
            {"op": "replace", "path": "/gender", "value": gender},
            {"op": "replace", "path": "/birthDate", "value": birthdate},
        ]

        # Update family name
        if "name" in related_person_data and isinstance(related_person_data["name"], list):
            for name in related_person_data["name"]:
                if "use" in name and name["use"] == "official":
                    if "family" in name:
                        patch_operations.append({"op": "replace", "path": f"/name/0/family", "value": family_name})

        # Update given names
        if "name" in related_person_data and isinstance(related_person_data["name"], list):
            for name in related_person_data["name"]:
                if "use" in name and name["use"] == "official":
                    if "given" in name:
                        patch_operations.append({"op": "replace", "path": f"/name/0/given", "value": given_names})

        # Update reference
        if "patient" in related_person_data:
            if "reference" in related_person_data["patient"]:
                patch_operations.append({"op": "replace", "path": "/patient/reference", "value": reference})

        # Update coding system, code, and display
        if "relationship" in related_person_data:
            if "coding" in related_person_data["relationship"]:
                for coding in related_person_data["relationship"]["coding"]:
                    if "system" in coding:
                        patch_operations.append({"op": "replace", "path": f"/relationship/coding/0/system", "value": code})
                    if "code" in coding:
                        patch_operations.append({"op": "replace", "path": f"/relationship/coding/0/code", "value": code})
                    if "display" in coding:
                        patch_operations.append({"op": "replace", "path": f"/relationship/coding/0/display", "value": display})

        # Apply the JSON Patch to update the fields
        patched_data = jsonpatch.apply_patch(related_person_data, patch_operations)

        # Convert the modified data back to JSON
        modified_json = json.dumps(patched_data, indent=4)
        return modified_json

    except Exception as e:
        return f"Error: {str(e)}"

def create_coverage_record(payload):
    file_path = os.path.join(fhir_samples_dir, "coverage.json")
    with open(file_path) as f:
        temp = json.load(f)
        data_template = json.dumps(temp)
        
        if not payload:
            record_payload = data_template
        else:
            # TODO: Check for errors
            record_payload = update_related_person_info(data_template, payload)
    return _create_record(record_payload, resource_type="Coverage")
    
def update_coverage_info(coverage_data, payload):
    # payload = {
    # "id": "9876C1", #this is coverage id, actually it will be automatically created
    #  # "beneficiary": {
    #     "reference": "Patient/patent_patient_id"
    # },
    # "beneficiary": {
    #     "reference": "Patient/new-beneficiary-id"
    # },
    # "dependent": "1",
    # "dependent_code": "child" # other options in FHIR R4 self, spouse, child, other 
    # }
    
    try:
        id_value = payload["id"]
        subscriber = payload["subscriber"]
        beneficiary = payload["beneficiary"]
        dependent = payload["dependent"]
        dependent_code = payload["dependent_code"]

        # Create a list of JSON Patch operations
        patch_operations = [
            {"op": "replace", "path": "/id", "value": id_value},
            {"op": "replace", "path": "/subscriber/reference", "value": subscriber},
            {"op": "replace", "path": "/beneficiary/reference", "value": beneficiary},
            {"op": "replace", "path": "/dependent", "value": dependent},
        ]

        # Update the "code" field in the "relationship" coding
        if "relationship" in coverage_data and "coding" in coverage_data["relationship"]:
            for coding in coverage_data["relationship"]["coding"]:
                if "code" in coding:
                    patch_operations.append({"op": "replace", "path": "/relationship/coding/0/code", "value": dependent_code})

        # Apply the JSON Patch to update the fields
        patched_data = jsonpatch.apply_patch(coverage_data, patch_operations)

        # Convert the modified data back to JSON
        modified_json = json.dumps(patched_data, indent=4)
        return modified_json

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    #create_patient_record()
    response = create_related_person_record()
    
    
    # token = get_fhir_access_token()
    # print(token)