# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
import decimal
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


# # Helper class for Dynamo
class DecimalEncoder(json.JSONEncoder):

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


# Try grab OS environment details from event
try:

    source_region = os.environ['ENV_SOURCE_REGION']
    table_name_multi = os.environ['ENV_TABLE_NAME_MULTI']
except Exception as e:
    print(f'No os.environment in lambda.... {e}')


# Try Assign dynamo table
try:

    db_client = boto3.resource('dynamodb', region_name=source_region)
    table = db_client.Table(table_name_multi)
except Exception as e:
    print(f'failed to speak to dynamo: {e}')


# Reply Message
def reply(message, status_code):

    return {
        'statusCode': str(status_code),
        'body': json.dumps(message, cls=DecimalEncoder),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
        },
    }


# Scan Entire Table DynamoDB
def scan_table():

    try:

        # Scan dynamo for all data
        current_items = table.scan(Select='ALL_ATTRIBUTES')
        data = current_items['Items']
        while 'LastEvaluatedKey' in current_items:
            current_items = table.scan(
                ExclusiveStartKey=current_items['LastEvaluatedKey'],
                Select='ALL_ATTRIBUTES')
            data.update(current_items['Items'])

        return current_items['Items']

    except ClientError as e:
        print('failed to scan dynamodb table...')
        print(e)


# Scan DynamoDB
def query_table(entry_type):

    try:

        # Scan dynamo for all Attribute data
        current_items = table.query(
            IndexName='EntryType-index',
            KeyConditionExpression=Key('EntryType').eq(entry_type))
        data = current_items['Items']
        while 'LastEvaluatedKey' in current_items:
            current_items = table.query(
                IndexName='EntryType-index',
                ExclusiveStartKey=current_items['LastEvaluatedKey'],
                KeyConditionExpression=Key('EntryType').eq(entry_type))
            data.update(current_items['Items'])

        return current_items['Items']

    except ClientError as e:
        print('failed to query dynamodb table...')
        print(e)


# Default lambda
def lambda_handler(event, context):

    try:

        print(json.dumps(event))

        # variables
        search_key = event['queryStringParameters']['scan']
        print(f'variable passed: {search_key}')

        if search_key == 'all':
            result = scan_table()
        else:
            result = query_table(entry_type=search_key)

        print(f'result: {result}')

        # create a response
        return reply(message=result, status_code=200)

    except ClientError as e:
        print('Unexpected error: %s' % e)
        return reply(message={'message': f'Error: {e}'}, status_code=500)
