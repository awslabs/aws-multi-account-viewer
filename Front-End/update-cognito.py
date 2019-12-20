# from os import path
import os
import boto3
import shutil

STACK_NAME = 'Multi-Account-Demo'

client = boto3.client('cloudformation')
response = client.describe_stacks(StackName=STACK_NAME)

# Grab Outputs
all_outputs = response['Stacks'][0]['Outputs']

# Grab Outputs from Cloudformation
for i in all_outputs:
    if i['ExportName'] == 'CognitoUserPool':
        export_userpool = i['OutputValue']
    if i['ExportName'] == 'CognitoUserPoolClient':
        export_userpoolclient = i['OutputValue']
    if i['ExportName'] == 'ApiGateWayEndPoint':
        export_apigateway = i['OutputValue']

# Create backup before trying to modify
shutil.copyfile('src/App.js', 'src/App-backup.js')

# Search for Existing values and replace
with open('src/App.js') as original, open('src/AppNew.js', 'w') as newfile:
    for line in original:
        if 'userPoolWebClientId:' in line:
            line = f'    userPoolWebClientId: "{export_userpoolclient}",\n'
            newfile.write(line)
        elif 'userPoolId:' in line:
            line = f'    userPoolId: "{export_userpool}",\n'
            newfile.write(line)
        elif 'endpoint:' in line:
            line = f'        endpoint: "{export_apigateway}",\n'
            newfile.write(line)
        else:
            newfile.write(line)

# Copy new file across
shutil.copyfile('src/AppNew.js', 'src/App.js')

# Delete old file
os.remove("src/AppNew.js")