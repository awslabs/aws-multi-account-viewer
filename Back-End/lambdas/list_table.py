import json
import os
import boto3
import decimal
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

# Helper class for Dynamo
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

# Try grab OS environment details
try:
    source_region = os.environ['ENV_SOURCE_REGION']
    table_name_multi = os.environ['ENV_TABLE_NAME_MULTI']
except Exception as e:
    print(f"No os.environment in lambda.... {e}")

# Try Assign dynamo table
try:
    dynamodb = boto3.resource('dynamodb', region_name=source_region)
    table = dynamodb.Table(table_name_multi)
except Exception as e:
    print(f"failed to speak to dynamo: {e}")
    

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

# Scan DynamoDB
def scan_table(entry_type):

    try:
        # Scan dynamo for all data
        current_items = table.scan(
            FilterExpression=Attr("EntryType").eq(entry_type)
        )

        return current_items

    except ClientError as e:
        print('failed to scan dynamodb table...')
        print(e)

# Default lambda
def lambda_handler(event, context):

    try:
        print(json.dumps(event))

        # variables
        search_key = event['queryStringParameters']['scan']
        print(f'variable passed: {search_key}')
        result = scan_table(entry_type=search_key)
        print(f'result: {result}')
        
        # create a response
        return reply(message=result['Items'], status_code=200)
        

    except ClientError as e:
        print("Unexpected error: %s" % e)
        return reply(message={'message': f'Error: {e}'}, status_code=500)
