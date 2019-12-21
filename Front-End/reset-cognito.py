# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import boto3
import shutil

export_userpool = 'ap-southeast-2_UsrPlId'
export_userpoolclient = '123usrPoolWebClientID456'
export_apigateway = 'https://abcd1234.execute-api.ap-southeast-2.amazonaws.com/prod'

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