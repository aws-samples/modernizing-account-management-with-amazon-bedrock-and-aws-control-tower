import json
import requests
import base64
import os

def lambda_handler(event, context):
    # Print the entire event
    print("Received event: " + json.dumps(event, indent=2))
    # Extract parameters from the event
    properties = event['requestBody']['content']['application/json']['properties']
    params = {prop['name']: prop['value'] for prop in properties}

    # GitHub repo details
    repo_owner = 'ebbsleo'
    repo_name = 'learn-terraform-aft-account-request'

    # GitHub credentials
    token = os.environ['GITHUB_TOKEN']
    commit_message = 'Append new Terraform module for ' + params['AccountName']

    # GitHub API URL for the Terraform file
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/terraform/main.tf'

    # Headers for GitHub API
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    # Check if the file exists and get its SHA
    response = requests.get(url, headers=headers, timeout=20)
    sha = response.json().get('sha') if response.ok else None
    existing_content = base64.b64decode(response.json()['content']).decode('utf-8') if sha else ""

    # Construct new module content from the event
    new_module_content = f'''
module "{params['AccountName']}" {{
  source = "./modules/aft-account-request"

  control_tower_parameters = {{
    AccountEmail              = "{params['AccountEmail']}"
    AccountName               = "{params['AccountName']}"
    ManagedOrganizationalUnit = "{params['ManagedOrganizationalUnit']}"
    SSOUserEmail              = "{params['AccountEmail']}"
    SSOUserFirstName          = "{params['SSOUserFirstName']}"
    SSOUserLastName           = "{params['SSOUserLastName']}"
  }}

  account_tags = {{
    "Learn Tutorial" = "AFT"
  }}

  change_management_parameters = {{
    change_requested_by = "{params['AccountName']}"
    change_reason       = "{params['ChangeReason']}"
  }}

  account_customizations_name = "{params['CustomizationName']}-{params['AccountName']}"
}}
'''

    # Append new module content to existing content
    updated_content = f"{existing_content}\n{new_module_content}"

    # Encode updated content to base64
    encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

    # Payload for GitHub API request
    data = {
        'message': commit_message,
        'content': encoded_content,
        'sha': sha
    }

    # Make PUT request to GitHub API to update the Terraform file
    put_response = requests.put(url, headers=headers, data=json.dumps(data), timeout=20)

    # Check the response from GitHub
    if put_response.status_code in [200, 201]:
        response_body = 'Module successfully appended to main.tf'
        http_status_code = 200
    else:
        response_body = put_response.json()
        http_status_code = put_response.status_code

    # Construct the API response
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup', ''),
            'apiPath': event.get('apiPath', ''),
            'httpMethod': event.get('httpMethod', ''),
            'httpStatusCode': http_status_code,
            'responseBody': response_body,
        },
        'sessionAttributes': event.get('sessionAttributes', {}),
        'promptSessionAttributes': event.get('promptSessionAttributes', {})
    }
