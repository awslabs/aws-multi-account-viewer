import boto3
import json
import os
import uuid
import re
import decimal
import copy
from ast import literal_eval
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

# event = {
#     "queryStringParameters": {
#         "function": "cron"
#     }
# }

# Helper class for Dynamo
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

# Try grab OS environment details
try:
    source_account = os.environ['ENV_SOURCE_ACCOUNT']
    source_region = os.environ['ENV_SOURCE_REGION']
    cross_account_role = os.environ['ENV_CROSS_ACCOUNT_ROLE']
    table_name_multi = os.environ['ENV_TABLE_NAME_MULTI']
    queue_url = os.environ['ENV_SQSQUEUE']
except Exception as e:
    print(f"No os.environment in lambda....: {e}")

# Try connect Clients
try:
    client_sqs = boto3.client('sqs', region_name=source_region)
    dynamodb = boto3.resource('dynamodb', region_name=source_region)
    table = dynamodb.Table(table_name_multi)
except Exception as e:
    print(f"failed to speak to dynamo or sqs....: {e}")

# Assume Role for sub accounts
def assume_sts_role(account_to_assume, cross_account_role_name):
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-api.html
    sts_client = boto3.client('sts')
    cross_account_role_arn = f"arn:aws:iam::{account_to_assume}:role/{cross_account_role_name}"

    try:

        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName="TemporaryRole"

        )["Credentials"]

        # Make temp creds
        temporary_credentials = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )

        # return creds
        return temporary_credentials

    except ClientError as e:
        print(
            f"Failed on Account: {account_to_assume} with Role: {cross_account_role_arn}")
        print(f"{cross_account_role_name} might not exists in account?")
        raise e

# Get Lambda Functions
def get_all_lambda(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_lambda = boto3.client('lambda', region_name=region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_lambda = assume_creds.client('lambda', region_name=region)
        print(f'Logged into Account: {account_number}')

    # Page all ec2
    paginator = client_lambda.get_paginator('list_functions')

    for page in paginator.paginate():
        for i in page['Functions']:

            # clean role name out of arn
            iam_role = str(i['Role']).split(':')[5].split('/')[1]

            var_list.append(
                {
                    'EntryType': 'lambda',
                    'Region': str(region),
                    'FunctionName': str(i['FunctionName']),
                    'FunctionArn': str(i['FunctionArn']),
                    'Runtime': str(i['Runtime']),
                    'AccountNumber': str(account_number),
                    'Timeout': str(i['Timeout']),
                    'RoleName': str(iam_role),
                    'MemorySize': str(i['MemorySize']),
                    'LastModified': str(i['LastModified'])
                })

    return var_list

# Get RDS Function
def get_all_rds(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_rds = boto3.client('rds', region_name=region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_rds = assume_creds.client('rds', region_name=region)
        print(f'Logged into Account: {account_number}')

    # Page all db instances
    paginator = client_rds.get_paginator('describe_db_instances')

    for page in paginator.paginate():
        for i in page['DBInstances']:
            #print(i)
            var_list.append(
                {   
                    'EntryType': 'rds',
                    'Region': str(region),
                    'AccountNumber': str(account_number),
                    'State': str(i['DBInstanceStatus']),
                    'DBInstanceIdentifier': i['DBInstanceIdentifier'],
                    'DBInstanceClass': i['DBInstanceClass'],
                    'Engine': i['Engine'],
                    'MultiAZ': i['MultiAZ'],
                    'PubliclyAccessible': i['PubliclyAccessible']
                })

    return var_list

# Get EC2 Function
def get_all_ec2(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_ec2 = boto3.client('ec2', region_name=region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_ec2 = assume_creds.client('ec2', region_name=region)
        print(f'Logged into Account: {account_number}')

    # Page all ec2
    paginator = client_ec2.get_paginator('describe_instances')

    for page in paginator.paginate():
        for i in page['Reservations']:

            # Check for IAM Role
            checkIAMrole = i['Instances'][0].get("IamInstanceProfile", " ")

            # Convert from string to dict if not empty
            if checkIAMrole != ' ':
                python_dict = literal_eval(f"{checkIAMrole}")
                full_role_name = python_dict['Arn']
                
                # clean role name out of arn
                iam_role = full_role_name.split(':')[5].split('/')[1]
            else:
                iam_role = ' '

            var_list.append(
                {
                    'EntryType': 'ec2',
                    'InstanceId': i['Instances'][0]['InstanceId'],
                    'State': i['Instances'][0]['State']['Name'],
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'KeyName': i['Instances'][0].get("KeyName", " "),
                    'RoleName': str(iam_role),
                    'PrivateIpAddress': i['Instances'][0].get("PrivateIpAddress", " "),
                    'PublicIpAddress': i['Instances'][0].get("PublicIpAddress", " "),
                    'InstancePlatform': i['Instances'][0].get('Platform', "Linux/UNIX"),
                    'InstanceType': i['Instances'][0]['InstanceType']
                })

    return var_list

# Get IAM Roles Function
def get_all_iam_roles(account_number):

    # Init
    var_list = []

    # Use boto3 on source account
    if account_number == source_account:
        iam_client = boto3.client('iam', region_name='us-east-1')
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        iam_client = assume_creds.client('iam', region_name='us-east-1')
        print(f'Logged into Account: {account_number}')

    # Page roles
    paginator = iam_client.get_paginator('list_roles')

    for page in paginator.paginate():         
        for i in page['Roles']:
            var_list.append(
                {
                    'Arn': str(i['Arn']),
                    'EntryType': 'iam-roles',
                    'Region': 'us-east-1',
                    'AccountNumber': str(account_number),
                    'RoleName': i['RoleName'],
                    'CreateDate': str(i['CreateDate'])
                })

    return var_list

# Get IAM Users Function
def get_all_iam_users(account_number):

    # Init
    var_list = []

    # Use boto3 on source account
    if account_number == source_account:
        iam_client = boto3.client('iam', region_name='us-east-1')
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        iam_client = assume_creds.client('iam', region_name='us-east-1')
        print(f'Logged into Account: {account_number}')

    # Page users
    paginator = iam_client.get_paginator('list_users')

    for page in paginator.paginate():         
        for i in page['Users']:
            var_list.append(
                {
                    'Arn': str(i['Arn']),
                    'EntryType': 'iam-users',
                    'AccountNumber': str(account_number),
                    'Region': 'us-east-1',
                    'UserName': str(i['UserName']),
                    'PasswordLastUsed': str(i.get("PasswordLastUsed", " ")),
                    'CreateDate': str(i['CreateDate'])
                })

    return var_list

# Get IAM Users Function
def get_all_iam_attached_policys(account_number):

    # Init
    var_list = []

    # Use boto3 on source account
    if account_number == source_account:
        iam_client = boto3.client('iam', region_name='us-east-1')
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        iam_client = assume_creds.client('iam', region_name='us-east-1')
        print(f'Logged into Account: {account_number}')

    # Page policys
    paginator = iam_client.get_paginator('list_policies')

    for page in paginator.paginate(OnlyAttached=True):         
        for i in page['Policies']:
            var_list.append(
                {
                    'Arn': str(i['Arn']),
                    'EntryType': 'iam-attached-policys',
                    'AccountNumber': str(account_number),
                    'Region': 'us-east-1',
                    'PolicyName': str(i['PolicyName']),
                    'AttachmentCount': int(i['AttachmentCount'])
                })

    return var_list

# Get OnDemand Capacity Reservations Function
def get_all_odcr(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_ec2 = boto3.client('ec2', region_name=region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_ec2 = assume_creds.client('ec2', region_name=region)
        print(f'Logged into Account: {account_number}')

    # Page all reservations
    paginator = client_ec2.get_paginator('describe_capacity_reservations')

    for page in paginator.paginate():
        for i in page['CapacityReservations']:
            if i['State'] == "active":
                var_list.append(
                    {
                    'EntryType': 'odcr',
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'AvailabilityZone': i['AvailabilityZone'],
                    'AvailableInstanceCount': i['AvailableInstanceCount'],
                    'CapacityReservationId': i['CapacityReservationId'],
                    'Qty Available': f"{i['AvailableInstanceCount']} of {i['TotalInstanceCount']}",
                    'CreateDate': str(i['CreateDate']),
                    'EbsOptimized': i['EbsOptimized'],
                    'EndDateType': str(i['EndDateType']),
                    'EphemeralStorage': i['EphemeralStorage'],
                    'InstanceMatchCriteria': i['InstanceMatchCriteria'],
                    'InstancePlatform': i['InstancePlatform'],
                    'InstanceType': i['InstanceType'],
                    'State': i['State'],
                    'Tags': i['Tags'],
                    'Tenancy': i['Tenancy'],
                    'TotalInstanceCount': i['TotalInstanceCount']
                 })

    return var_list

# Get Organizations Function
def get_organizations(account_number):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_org = boto3.client('organizations')
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_org = assume_creds.client('organizations')
        print(f'Logged into Account: {account_number}')

    # Page all org
    paginator = client_org.get_paginator('list_accounts')

    for page in paginator.paginate():
        for i in page['Accounts']:
            if i['Status'] == "ACTIVE":
                var_list.append(
                    {
                    'AccountNumber': str(i['Id']),
                    'Arn': str(i['Arn']),
                    'Region': 'us-east-1',
                    'EntryType': 'org',
                    'Name': str(i['Name']),
                    'Email': str(i['Email']),
                    'Status': i['Status']
                 })

    return var_list

# Get VPC Function
def get_all_vpc(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_ec2 = boto3.client('ec2', region_name=region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_ec2 = assume_creds.client('ec2', region_name=region)
        print(f'Logged into Account: {account_number}')

    # Page all vpc's
    paginator = client_ec2.get_paginator('describe_vpcs')

    for page in paginator.paginate():
        for i in page['Vpcs']:
            #print(i)
            var_list.append(
                {   
                    'EntryType': 'vpc',
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'CidrBlock': str(i['CidrBlock']),
                    'VpcId': str(i['VpcId']),
                    'DhcpOptionsId': i['DhcpOptionsId'],
                    'InstanceTenancy': i['InstanceTenancy']
                })

    return var_list

# Get Subnet Function
def get_all_subnets(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_ec2 = boto3.client('ec2', region_name=region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_ec2 = assume_creds.client('ec2', region_name=region)
        print(f'Logged into Account: {account_number}')

    # No paginator for subnets
    # paginator = client_ec2.get_paginator('describe_subnets')
    result = client_ec2.describe_subnets()

    for i in result['Subnets']:
        #print(i)
        var_list.append(
            {   
                'EntryType': 'subnet',
                'AccountNumber': str(account_number),
                'Region': region,
                'CidrBlock': str(i['CidrBlock']),
                'AvailabilityZone': i['AvailabilityZone'],
                'AvailabilityZoneId': i['AvailabilityZoneId'],
                'SubnetId': str(i['SubnetId']),
                'VpcId': str(i['VpcId']),
                'SubnetArn': str(i['SubnetArn']),
                'AvailableIpAddressCount': i['AvailableIpAddressCount']
            })

    return var_list

# Get Reserved Instances
def get_all_ris(account_number, region):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_ec2 = boto3.client('ec2')
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_ec2 = assume_creds.client('ec2')
        print(f'Logged into Account: {account_number}')

    # No paginator for reservations
    # paginator = client_ec2.get_paginator('')
    result = client_ec2.describe_reserved_instances()

    for i in result['ReservedInstances']:
        # only get active ones
        if i['State'] == 'active':
            var_list.append(
                {   
                    'EntryType': 'ri',
                    'AccountNumber': str(account_number),
                    'InstanceCount': str(i['InstanceCount']),
                    'InstanceType': i['InstanceType'],
                    'Scope': i['Scope'],
                    'ProductDescription': str(i['ProductDescription']),
                    'ReservedInstancesId': str(i['ReservedInstancesId']),
                    'Start': str(i['Start']),
                    'End': str(i['End']),
                    'InstanceTenancy': i['InstanceTenancy'],
                    'OfferingClass': i['OfferingClass']
                })

    return var_list

# Get S3 Buckets
def get_all_s3_buckets(account_number):

    # Init
    var_list = []

     # Use boto3 on source account
    if account_number == source_account:
        client_s3 = boto3.client('s3', region_name='us-east-1')
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client_s3 = assume_creds.client('s3', region_name='us-east-1')
        print(f'Logged into Account: {account_number}')

    # No paginator for listing buckets
    # paginator = client_ec2.get_paginator('')
    result = client_s3.list_buckets()

    for i in result['Buckets']:
        var_list.append(
            {   
                'Name': str(i['Name']),
                'EntryType': 's3-buckets',
                'AccountNumber': str(account_number),
                'Region': 'us-east-1',
                'CreationDate': str(i['CreationDate'])
            })

    return var_list


### DynamoDB ###

# Get data sitting in DynamoDB for each account
def get_current_table(account_number, entry_type, region):

    try:
        # Scan dynamo for all data
        response = table.scan(
            FilterExpression=Attr("AccountNumber").eq(account_number) & Attr("EntryType").eq(str(entry_type)) & Attr("Region").eq(str(region)))

        print(f"items from db scan: {response['Items']}")
        return response['Items']

    except ClientError as e:
        print('failed to scan dynamodb table...')
        print(e)

# DynamoDB Get Item
def dynamo_get_item(dynamodb_item):

    try:
        response = table.get_item(Key={'Id': str(dynamodb_item['Id']) })
        print(f"Sucessfully got {dynamodb_item}")

        if 'Item' in response:
            return response['Item']
        else:
            return None

    except ClientError as e:
        print("Unexpected error: %s" % e)
 
# DynamoDB Create Item
def dynamo_create_item(dynamodb_item):

    try:

        response = table.put_item(Item=dynamodb_item)

        print(f"Sucessfully added {dynamodb_item}")
        return response

    except ClientError as e:
        print("Unexpected error: %s" % e)

# DynamoDB Delete Item
def dynamo_delete_item(dynamodb_item):

    try:

        response = table.delete_item(
            Key={
                'Id': dynamodb_item
            })

        print(f"Sucessfully deleted {dynamodb_item}")
        return response

    except ClientError as e:
        print(f"FAILED ON ID: {dynamodb_item}")
        print("Unexpected error: %s" % e)

# delete all items in table  | function not used |
def dynamo_delete_all_items():
    scan = table.scan(
        ProjectionExpression='#k',
        ExpressionAttributeNames={
            '#k': 'Id'
        }
    )

    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(Key=each)

# compare lists in dynamodb and boto3 calls
def compare_lists_and_update(boto_list, dynamo_list, pop_list):

    # remove Id key to compare current boto calls
    for i in pop_list:
        i.pop('Id')

    if len(boto_list) >= 1:
        for r in boto_list:
            if r not in pop_list:
                print('new item, updating entries now...')
                r.update({'Id': str(uuid.uuid4())})
                dynamo_create_item(r)
            else:
                print('no update needed...')
    else:
        # Boto list has no values
        print('list empty, skipping')

    if len(dynamo_list) >= 1:
        for i in dynamo_list:
            old_id = i['Id']
            i.pop('Id')
            if i not in boto_list:
                print('deleting entry as not current or present in boto call')
                i.update({'Id': old_id})
                dynamo_delete_item(i['Id'])
            else:
                print('item is in boto list, skipping')
    else:
        # Boto list has no values
        print('list empty, skipping')

# Reply message
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

### Logic for each service ####

# Logic for Lambda
def handle_message_lambda(account_number, region):
    print('printing event....')

    # init
    lambda_list = []
    dynamo_lambda_list = []
    pop_dynamo = []

    # get current lambdas
    lambda_list = get_all_lambda(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_lambda_list = get_current_table(account_number=account_number, entry_type='lambda', region=region)

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_lambda_list)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=lambda_list, dynamo_list=dynamo_lambda_list, pop_list=pop_dynamo)
    
# Logic for RDS
def handle_message_rds(account_number, region):
    print('printing event....')

    # init
    rds_list = []
    dynamo_rds_list = []
    pop_dynamo = []

    # get current rds
    rds_list = get_all_rds(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_rds_list = get_current_table(account_number=account_number, entry_type='rds', region=region)

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_rds_list)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=rds_list, dynamo_list=dynamo_rds_list, pop_list=pop_dynamo)

# Logic for EC2
def handle_message_ec2(account_number, region):
    print('printing event....')

    # init
    ec2_list = []
    dynamo_ec2_list = []
    pop_dynamo = []

    # Get current ec2
    ec2_list = get_all_ec2(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_ec2_list = get_current_table(account_number=account_number, entry_type='ec2', region=region)

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_ec2_list)

    #remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=ec2_list, dynamo_list=dynamo_ec2_list, pop_list=pop_dynamo)

# Logic for IAM Roles
def handle_message_iam_role(account_number):
    print('printing event....')

    # init
    roles = []
    dynamo_roles = []
    pop_dynamo = []

    # get current roles
    roles = get_all_iam_roles(account_number=account_number)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_roles = get_current_table(account_number=account_number, entry_type='iam-roles', region='us-east-1')

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_roles)

    # Check and compare unique entry for whats currently in boto3 iam list and whats in dynamodb
    compare_lists_and_update(boto_list=roles, dynamo_list=dynamo_roles, pop_list=pop_dynamo)

# Logic for IAM Users
def handle_message_iam_users(account_number):
    print('printing event....')

    # init
    users = []
    dynamo_users = []
    pop_dynamo = []

    # get current users
    users = get_all_iam_users(account_number=account_number)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_users = get_current_table(account_number=account_number, entry_type='iam-users', region='us-east-1')

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_users)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=users, dynamo_list=dynamo_users, pop_list=pop_dynamo)

# Logic for IAM List Policys
def handle_message_iam_attached_policys(account_number):
    print('printing event....')

    # init
    current_policys = []
    dynamo_policys = []
    pop_dynamo = []

    # Get current policys
    current_policys = get_all_iam_attached_policys(account_number=account_number)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_policys = get_current_table(account_number=account_number, entry_type='iam-attached-policys', region='us-east-1')

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_policys)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=current_policys, dynamo_list=dynamo_policys, pop_list=pop_dynamo)

# Logic for OnDemand Capacity Reservations
def handle_message_odcr(account_number, region):
    print('printing event....')

    # init
    odcr_list = []
    dynamo_odcr_list = []
    pop_dynamo = []

    # get current odcr
    odcr_list = get_all_odcr(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_odcr_list = get_current_table(account_number=account_number, entry_type='odcr', region=region)

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_odcr_list)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=odcr_list, dynamo_list=dynamo_odcr_list, pop_list=pop_dynamo)

# Logic for Organizations
def handle_message_organizations(account_number):
    print('printing event....')

    # init
    org_list = []
    dynamo_org_list = []
    pop_dynamo = []

    # get current Org
    org_list = get_organizations(account_number=account_number)

    # This entry can't use normal scan function because organizations calls are already multi account
    dynamo_org_list = table.scan(
        FilterExpression=Attr("EntryType").eq("org")
        )['Items']

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_org_list)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=org_list, dynamo_list=dynamo_org_list, pop_list=pop_dynamo)

# Logic for VPC
def handle_message_vpc(account_number, region):
    print('printing event....')

    # init
    vpc_list = []
    dynamo_vpc_list = []
    pop_dynamo = []

    # get current vpcs
    vpc_list = get_all_vpc(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_vpc_list = get_current_table(account_number=account_number, entry_type='vpc', region=region)
    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_vpc_list)
    # pop_dynamo = get_current_table(account_number=account_number, entry_type='vpc', region=region)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=vpc_list, dynamo_list=dynamo_vpc_list, pop_list=pop_dynamo)

# Logic for Subnets
def handle_message_subnets(account_number, region):
    print('printing event....')

    # init
    subnet_list = []
    dynamo_subnet_list = []
    pop_dynamo = []

    # get current subnets
    subnet_list = get_all_subnets(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_subnet_list = get_current_table(account_number=account_number, entry_type='subnet', region=region)
    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_subnet_list)
    # pop_dynamo = get_current_table(account_number=account_number, entry_type='subnet', region=region)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=subnet_list, dynamo_list=dynamo_subnet_list, pop_list=pop_dynamo)

# Logic for RI's
def handle_message_ris(account_number, region):
    print('printing event....')

    # init
    ri_list = []
    dynamo_ri_list = []
    pop_dynamo = []

    # get current ris
    ri_list = get_all_ris(account_number=account_number, region=region)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_ri_list = get_current_table(account_number=account_number, entry_type='ri', region=region)

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_ri_list)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=ri_list, dynamo_list=dynamo_ri_list, pop_list=pop_dynamo)

# Logic for S3 Buckets
def handle_message_s3_buckets(account_number):
    print('printing event....')

    # init
    s3_list = []
    dynamo_s3_list = []
    pop_dynamo = []

    # get current s3 buckets
    s3_list = get_all_s3_buckets(account_number=account_number)

    # Get current data sitting in Dynamo and remove inactive entries
    dynamo_s3_list = get_current_table(account_number=account_number, entry_type='s3-buckets', region='us-east-1')

    # Deep copy instead of double dynamo read
    pop_dynamo = copy.deepcopy(dynamo_s3_list)

    # remove Id key from dynamodb item and check if value has changed.
    compare_lists_and_update(boto_list=s3_list, dynamo_list=dynamo_s3_list, pop_list=pop_dynamo)


# Default Lambda
def lambda_handler(event, context):

    print(json.dumps(event))

    # message hasn't failed yet
    failed = False

    try:
        message = event['Records'][0]
    except KeyError:
        print('No messages on the queue!')

    try:
        message = event['Records'][0]
        print(json.dumps(message))
        function = message['messageAttributes']['Function']['stringValue']
        account_number = message['messageAttributes']['AccountNumber']['stringValue']
        region = message['messageAttributes']['Region']['stringValue']
        receipt_handle = event['Records'][0]['receiptHandle']

        print(f'function passed is: {function}')

        # Do something with each function:
        if function == 'lambda':
            handle_message_lambda(account_number, region)
        if function == 'ec2':
            handle_message_ec2(account_number, region)
        if function == 'rds':
            handle_message_rds(account_number, region)
        if function == 'iam-roles':
            handle_message_iam_role(account_number)
        if function == 'iam-users':
            handle_message_iam_users(account_number)
        if function == 'iam-attached-policys':
            handle_message_iam_attached_policys(account_number)
        if function == 'odcr':
            handle_message_odcr(account_number, region)
        if function == 'org':
            handle_message_organizations(account_number)
        if function == 'vpc':
            handle_message_vpc(account_number, region)
        if function == 'subnet':
            handle_message_subnets(account_number, region)
        if function == 'ri':
            handle_message_ris(account_number, region)
        if function == 's3-buckets':
            handle_message_s3_buckets(account_number)

        # Stop/Start instance function:
        if function == 'rds-stop':
            handle_message_rds(account_number, region)

    except ClientError as e:
        print('failed to process message')
        print(e)
        failed = True

    # message must have passed, delete from queue
    if failed == False:
        # The message was handled successfully. We can delete it now.
        client_sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )