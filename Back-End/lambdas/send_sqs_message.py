# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import os
import decimal
from botocore.exceptions import ClientError

# Helper class for Dynamo
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

# Try grab OS environment details
try:
    accNumbers = os.environ['ENV_ACCOUNTS']
    source_account = os.environ['ENV_SOURCE_ACCOUNT']
    source_region = os.environ['ENV_SOURCE_REGION']
    regions = os.environ['ENV_REGIONS']
    cross_account_role = os.environ['ENV_CROSS_ACCOUNT_ROLE']
    queue_url = os.environ['ENV_SQSQUEUE']
except Exception as e:
    print(f"No os.environment in lambda.... {e}")

# Try connect sqs
try:
    sqs = boto3.client('sqs', region_name=source_region)
except Exception as e:
    print(f"cant connect to sqs.... {e}")

def reply(message, status_code):

    return {
        'statusCode': str(status_code),
        'body': json.dumps(message, cls=DecimalEncoder),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
    }

# Send message to SQS queue
def send_sqs_message(accountNumber, function, region):

    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=0,
        MessageAttributes={
            'AccountNumber': {
                'DataType': 'String',
                'StringValue': f'{accountNumber}'
            },
            'Function': {
                'DataType': 'String',
                'StringValue': f'{function}'
            },
            'Region': {
                'DataType': 'String',
                'StringValue': f'{region}'
            }
        },
        MessageBody=(
            f'account: {accountNumber} with function: {function} in region: {region}'
        )
    )

    return response


def lambda_handler(event, context):

    try:

        print(json.dumps(event))
        passed_function = event['queryStringParameters']['function']
        print(f'function is {passed_function}')

        # Get Accounts
        list_of_accounts = []
        for a in accNumbers.split(','):
            list_of_accounts.append(a)

        # Get Regions
        list_of_regions = []
        for b in regions.split(','):
            list_of_regions.append(b)

        # Global API that don't need to hit every region, e.g IAM, S3 etc
        global_api = ['iam-roles', 'iam-users', 'iam-attached-policys', 's3-buckets']

        # if cron, send all messages to all accounts
        if passed_function == 'cron':

            for i in list_of_accounts:

                # Global API, don't hit each region
                send_sqs_message(accountNumber=i, function='iam-roles', region='us-east-1')
                send_sqs_message(accountNumber=i, function='iam-users', region='us-east-1')
                send_sqs_message(accountNumber=i, function='iam-attached-policys', region='us-east-1')
                send_sqs_message(accountNumber=i, function='s3-buckets', region='us-east-1')

                for b in list_of_regions:

                    print(f'sending account: {i} into region: {b}')
                    send_sqs_message(accountNumber=i, function='lambda', region=b)
                    send_sqs_message(accountNumber=i, function='ec2', region=b)
                    send_sqs_message(accountNumber=i, function='rds', region=b)
                    send_sqs_message(accountNumber=i, function='odcr', region=b)
                    send_sqs_message(accountNumber=i, function='lightsail', region=b)
                    send_sqs_message(accountNumber=i, function='vpc', region=b)
                    send_sqs_message(accountNumber=i, function='subnet', region=b)
                    send_sqs_message(accountNumber=i, function='ri', region=b)

        # if function is organizations
        elif passed_function == 'org':
            send_sqs_message(accountNumber=source_account, function='org', region='us-east-1')

        # if function is global and doesn't need each region
        elif passed_function in global_api:
            for i in list_of_accounts:
                send_sqs_message(accountNumber=i, function=passed_function, region='us-east-1')

        # Else send the function to all accounts
        else:

            for i in list_of_accounts:

                # Do rest of calls in list of regions
                for b in list_of_regions:
                    print(f'sending region: {b}')
                    send_sqs_message(accountNumber=i, function=passed_function, region=b)
        
        # Reply back
        return reply(message='sucessfully passed message to sqs', status_code=200)

    except ClientError as e:
        print("Unexpected error: %s" % e)
        return reply(message={'message': f'Error: {e}'}, status_code=500)