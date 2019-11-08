# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import os
import uuid
import decimal
import copy
from ast import literal_eval
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr, Key


# Helper class for Dynamo
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202
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
    print(f'Error: No os.environment in lambda....: {e}')


# Try connect Clients
try:
    client_sqs = boto3.client('sqs', region_name=source_region)
    dynamodb = boto3.resource('dynamodb', region_name=source_region)
    table = dynamodb.Table(table_name_multi)
except Exception as e:
    print(f'Error: failed to speak to dynamo or sqs....: {e}')


# event = {
#     'queryStringParameters': {
#         'function': 'cron'
#     }
# }


# Assume Role for sub accounts
def assume_sts_role(account_to_assume, cross_account_role_name):

    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-api.html
    sts_client = boto3.client('sts')
    cross_account_role_arn = f'arn:aws:iam::{account_to_assume}:role/{cross_account_role_name}'

    try:

        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRole'

        )['Credentials']

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
            f'Error: on Account: {account_to_assume} with Role: {cross_account_role_arn}')
        print(f'{cross_account_role_name} might not exists in account?')
        raise e


# Create Boto Client
def create_boto_client(account_number, region, service, cross_account_role):

    # Use boto3 on source account
    if account_number == source_account:
        client = boto3.client(service, region)
        print(f'skipping STS for local account: {account_number}')

    else:
        # Log into Accounts with STS
        assume_creds = assume_sts_role(account_number, cross_account_role)
        client = assume_creds.client(service, region)
        print(f'Logged into Account: {account_number}')

    return client


# Get Lambda Functions
def get_all_lambda(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Change boto client
    client_lambda = create_boto_client(
        account_number, region, 'lambda', cross_account_role)

    # Page all ec2
    paginator = client_lambda.get_paginator('list_functions')

    for page in paginator.paginate():
        for i in page['Functions']:

            # clean role name out of arn
            iam_role = str(i['Role']).split(':')[5].split('/')[1]

            # Get tags
            lambda_arn = i['FunctionArn']
            lambda_tag = client_lambda.list_tags(Resource=lambda_arn)['Tags']

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
                    'Handler': str(i['Handler']),
                    'CodeSize': int(i['CodeSize']),
                    'Version': str(i['Version']),
                    'MemorySize': int(i['MemorySize']),
                    'LastModified': str(i['LastModified']),
                    'Tags': str(lambda_tag)
                })

    return var_list


# Get RDS Function
def get_all_rds(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Change boto client
    client_rds = create_boto_client(
        account_number, region, 'rds', cross_account_role)

    # Page all db instances
    paginator = client_rds.get_paginator('describe_db_instances')

    for page in paginator.paginate():
        for i in page['DBInstances']:

            # Get tags
            instance = i['DBInstanceArn']
            rds_tag = client_rds.list_tags_for_resource(
                ResourceName=instance)['TagList']

            var_list.append(
                {
                    'EntryType': 'rds',
                    'Region': str(region),
                    'AccountNumber': str(account_number),
                    'State': str(i['DBInstanceStatus']),
                    'DBInstanceIdentifier': str(i['DBInstanceIdentifier']),
                    'DBInstanceClass': str(i['DBInstanceClass']),
                    'AllocatedStorage': int(i.get('AllocatedStorage', ' ')),
                    'PreferredBackupWindow': str(i.get('PreferredBackupWindow', ' ')),
                    'BackupRetentionPeriod': str(i.get('BackupRetentionPeriod', ' ')),
                    'PreferredMaintenanceWindow': str(i.get('PreferredMaintenanceWindow', ' ')),
                    'StorageType': str(i.get('StorageType', ' ')),
                    'Engine': str(i['Engine']),
                    'MultiAZ': str(i.get('MultiAZ', ' ')),
                    'PubliclyAccessible': str(i.get('PubliclyAccessible', ' ')),
                    'Tags': str(rds_tag)
                })

    return var_list


# Get EKS Function
def get_all_eks(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Change boto client
    client_eks = create_boto_client(
        account_number, region, 'eks', cross_account_role)

    # Get all eks clusters
    paginator = client_eks.get_paginator('list_clusters')

    for page in paginator.paginate():
        for i in page['clusters']:

            cluster_name = i
            eks_detail = client_eks.describe_cluster(name=cluster_name)['cluster']
            # cluster_arn = eks_detail['arn']
            # eks_tags = client_eks.list_tags_for_resource(
            #     resourceArn=cluster_arn)['tags']

            var_list.append({
                'AccountNumber': str(account_number),
                'EntryType': str('eks'),
                'Region': str(region),
                'Name': str(eks_detail['name']),
                'Arn': str(eks_detail['arn']),
                'Status': str(eks_detail['status']),
                'RoleArn': str(eks_detail.get('roleArn', ' ')),
                'Created': str(eks_detail['createdAt']),
                'VpcId': str(eks_detail['resourcesVpcConfig'].get('vpcId', ' ')),
                'PlatformVersion': str(eks_detail['platformVersion']),
                'K8 Version': str(eks_detail['version']),
                'Endpoint': str(eks_detail['endpoint'])
                # 'Tags': str(eks_tags)
            })

        return var_list


# Get EC2 Function
def get_all_ec2(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    # Page all ec2
    paginator = client_ec2.get_paginator('describe_instances')

    for page in paginator.paginate():
        for i in page['Reservations']:

            # Check for IAM Role
            checkIAMrole = i['Instances'][0].get('IamInstanceProfile', ' ')

            # Convert from string to dict if not empty
            if checkIAMrole != ' ':
                python_dict = literal_eval(f'{checkIAMrole}')
                full_role_name = python_dict['Arn']

                # clean role name out of arn
                iam_role = full_role_name.split(':')[5].split('/')[1]
            else:
                iam_role = ' '

            # Get vCPU count
            vcpu_core = i['Instances'][0]['CpuOptions']['CoreCount']
            vcpu_thread = i['Instances'][0]['CpuOptions']['ThreadsPerCore']

            # Cores x thread = vCPU count
            vCPU = int(vcpu_core) * int(vcpu_thread)

            # Turn Tags into Strings for Table format on front end
            ec2_tags = i['Instances'][0].get('Tags', ' ')

            var_list.append(
                {
                    'EntryType': 'ec2',
                    'InstanceId': str(i['Instances'][0]['InstanceId']),
                    'State': str(i['Instances'][0]['State']['Name']),
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'vCPU': int(vCPU),
                    'KeyName': str(i['Instances'][0].get('KeyName', ' ')),
                    'RoleName': str(iam_role),
                    'PrivateIpAddress': str(i['Instances'][0].get('PrivateIpAddress', ' ')),
                    'PublicIpAddress': str(i['Instances'][0].get('PublicIpAddress', ' ')),
                    'InstancePlatform': str(i['Instances'][0].get('Platform', 'Linux/UNIX')),
                    'InstanceType': str(i['Instances'][0]['InstanceType']),
                    'Tags': str(ec2_tags)
                })

    return var_list


# Get IAM Roles Function
def get_all_iam_roles(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_iam = create_boto_client(
        account_number, region, 'iam', cross_account_role)

    # Page roles
    paginator = client_iam.get_paginator('list_roles')

    for page in paginator.paginate():
        for i in page['Roles']:
            var_list.append(
                {
                    'Arn': str(i['Arn']),
                    'EntryType': 'iam-roles',
                    'Region': 'us-east-1',
                    'AccountNumber': str(account_number),
                    'RoleName': str(i['RoleName']),
                    'CreateDate': str(i['CreateDate'])
                })

    return var_list


# Get IAM Users Function
def get_all_iam_users(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_iam = create_boto_client(
        account_number, region, 'iam', cross_account_role)

    # Page users
    paginator = client_iam.get_paginator('list_users')

    for page in paginator.paginate():
        for i in page['Users']:
            var_list.append(
                {
                    'Arn': str(i['Arn']),
                    'EntryType': 'iam-users',
                    'AccountNumber': str(account_number),
                    'Region': 'us-east-1',
                    'UserName': str(i['UserName']),
                    'PasswordLastUsed': str(i.get('PasswordLastUsed', ' ')),
                    'CreateDate': str(i['CreateDate'])
                })

    return var_list


# Get IAM Users Function
def get_all_iam_attached_policys(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_iam = create_boto_client(
        account_number, region, 'iam', cross_account_role)

    # Page policys
    paginator = client_iam.get_paginator('list_policies')

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
def get_all_odcr(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    # Page all reservations
    paginator = client_ec2.get_paginator('describe_capacity_reservations')

    for page in paginator.paginate():
        for i in page['CapacityReservations']:
            if i['State'] == 'active':
                var_list.append(
                    {
                        'EntryType': 'odcr',
                        'AccountNumber': str(account_number),
                        'Region': str(region),
                        'AvailabilityZone': str(i['AvailabilityZone']),
                        'AvailableInstanceCount': int(i['AvailableInstanceCount']),
                        'CapacityReservationId': str(i['CapacityReservationId']),
                        'Qty Available': str(f"{i['AvailableInstanceCount']} of {i['TotalInstanceCount']}"),
                        'CreateDate': str(i['CreateDate']),
                        'EbsOptimized': str(i['EbsOptimized']),
                        'EndDateType': str(i['EndDateType']),
                        'EphemeralStorage': str(i['EphemeralStorage']),
                        'InstanceMatchCriteria': str(i['InstanceMatchCriteria']),
                        'InstancePlatform': str(i['InstancePlatform']),
                        'InstanceType': str(i['InstanceType']),
                        'State': str(i['State']),
                        'Tags': str(i['Tags']),
                        'Tenancy': str(i['Tenancy']),
                        'TotalInstanceCount': int(i['TotalInstanceCount'])
                    })

    return var_list


# Get Lightsail Instances Function
def get_all_lightsail(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_lightsail = create_boto_client(
        account_number, region, 'lightsail', cross_account_role)

    # Page all reservations
    paginator = client_lightsail.get_paginator('get_instances')

    for page in paginator.paginate():
        for i in page['instances']:
            var_list.append(
                {
                    'EntryType': 'lightsail',
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'AvailabilityZone': str(i['location']['availabilityZone']),
                    'Name': str(i['name']),
                    'CreateDate': str(i['createdAt']),
                    'Blueprint': str(i['blueprintName']),
                    'RAM in GB': int(i['hardware']['ramSizeInGb']),
                    'vCPU': int(i['hardware']['cpuCount']),
                    'SSD in GB': int(i['hardware']['disks'][0]['sizeInGb']),
                    'Public IP': str(i['publicIpAddress'])
                })

    return var_list


# Get Organizations Function
def get_organizations(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_org = create_boto_client(
        account_number, region, 'organizations', cross_account_role)

    # Page all org
    paginator = client_org.get_paginator('list_accounts')

    for page in paginator.paginate():
        for i in page['Accounts']:
            if i['Status'] == 'ACTIVE':
                var_list.append(
                    {
                        'AccountNumber': str(i['Id']),
                        'Arn': str(i['Arn']),
                        'Region': 'us-east-1',
                        'EntryType': 'org',
                        'Name': str(i['Name']),
                        'Email': str(i['Email']),
                        'Status': str(i['Status']),
                        'JoinedMethod': str(i['JoinedMethod'])
                    })

    return var_list


# Get VPC Function
def get_all_vpc(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    # Page all vpc's
    paginator = client_ec2.get_paginator('describe_vpcs')

    for page in paginator.paginate():
        for i in page['Vpcs']:
            var_list.append(
                {
                    'EntryType': 'vpc',
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'CidrBlock': str(i['CidrBlock']),
                    'VpcId': str(i['VpcId']),
                    'DhcpOptionsId': str(i['DhcpOptionsId']),
                    'InstanceTenancy': str(i['InstanceTenancy']),
                    'Tags': str(i.get('Tags', ' '))
                })

    return var_list


# Get All Network Interfaces Function
def get_all_network_interfaces(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    # Page all vpc's
    paginator = client_ec2.get_paginator('describe_network_interfaces')

    for page in paginator.paginate():
        for i in page['NetworkInterfaces']:
            var_list.append(
                {
                    'EntryType': 'network-interfaces',
                    'PrivateIpAddress': str(i.get('PrivateIpAddress', ' ')),
                    'PublicIp': str(i.get('Association', {}).get('PublicIp', ' ')),
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'Status': str(i.get('Status', ' ')),
                    'AttStatus': str(i.get('Attachment', {}).get('Status', ' ')),
                    'InterfaceType': str(i.get('InterfaceType', ' ')),
                    'NetworkInterfaceId': str(i.get('NetworkInterfaceId', ' ')),
                    'Description': str(i.get('Description', ' '))
                })

    return var_list


# Get Subnet Function
def get_all_subnets(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    # No paginator for subnets
    # paginator = client_ec2.get_paginator('describe_subnets')
    result = client_ec2.describe_subnets()

    for i in result['Subnets']:
        var_list.append(
            {
                'EntryType': 'subnet',
                'AccountNumber': str(account_number),
                'Region': region,
                'CidrBlock': str(i['CidrBlock']),
                'AvailabilityZone': str(i['AvailabilityZone']),
                'AvailabilityZoneId': str(i['AvailabilityZoneId']),
                'SubnetId': str(i['SubnetId']),
                'VpcId': str(i['VpcId']),
                'SubnetArn': str(i['SubnetArn']),
                'AvailableIpAddressCount': i['AvailableIpAddressCount'],
                'Tags': str(i.get('Tags', ' '))
            })

    return var_list


# Get Reserved Instances
def get_all_ris(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

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
                    'InstanceCount': int(i['InstanceCount']),
                    'InstanceType': str(i['InstanceType']),
                    'Scope': str(i['Scope']),
                    'ProductDescription': str(i['ProductDescription']),
                    'ReservedInstancesId': str(i['ReservedInstancesId']),
                    'Start': str(i['Start']),
                    'End': str(i['End']),
                    'InstanceTenancy': str(i['InstanceTenancy']),
                    'OfferingClass': str(i['OfferingClass'])
                })

    return var_list


# Get S3 Buckets
def get_all_s3_buckets(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_s3 = create_boto_client(
        account_number, region, 's3', cross_account_role)

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


# Get data sitting in DynamoDB for each account
def get_current_table(account_number, entry_type, region):

    try:
        # Scan dynamo for all data
        response = table.query(
            IndexName='EntryType-index',
            KeyConditionExpression=Key('EntryType').eq(entry_type),
            FilterExpression=Attr('AccountNumber').eq(account_number) &
            Attr('Region').eq(region)
        )

        print(f"items from db query: {response['Items']}")
        return response['Items']

    except ClientError as e:
        print(f'Error: failed to query dynamodb table... {e}')
    except Exception as e:
        print(f'Error: failed to query dynamodb table...{e}')


# Get data sitting in DynamoDB without account look up
def get_current_table_without_account(entry_type, region):

    try:
        # Scan dynamo for all data
        response = table.query(
            IndexName='EntryType-index',
            KeyConditionExpression=Key('EntryType').eq(entry_type),
            FilterExpression=Attr('Region').eq(region)
        )

        print(f"items from db query: {response['Items']}")
        return response['Items']

    except ClientError as e:
        print(f'Error: failed to query dynamodb table...{e}')
    except Exception as e:
        print(f'Error: failed to query dynamodb table...{e}')


# DynamoDB Create Item
def dynamo_create_item(dynamodb_item):

    try:

        # Put item
        response = table.put_item(Item=dynamodb_item)

        print(f'Sucessfully added {dynamodb_item}')
        return response

    except ClientError as e:
        print(f'Error: failed to add {dynamodb_item} - {e}')
    except Exception as e:
        print(f'Error: creating item {dynamodb_item} - {e}')


# DynamoDB Delete Item
def dynamo_delete_item(dynamodb_item):

    try:

        response = table.delete_item(
            Key={
                'Id': dynamodb_item
            })

        print(f'Sucessfully deleted {dynamodb_item}')
        return response

    except ClientError as e:
        print(f'Error: Failed ON ID: {dynamodb_item} - {e}')


# delete all items in table, function not used but good for testing
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
                # Strip empty values
                strip_empty_values = {k: v for k, v in r.items() if v}
                dynamo_create_item(strip_empty_values)
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


# Logic to compare what current boto see's vs whats in dynamodb
def compare_and_update_function(account_number, region, sqs_function, cross_account_role):
    print('printing event....')

    try:
        # init
        current_boto_list = []
        dynamo_list = []
        pop_dynamo = []

        # Get Current Boto Data
        if sqs_function == 'lambda':
            current_boto_list = get_all_lambda(
                account_number, region, cross_account_role)
        elif sqs_function == 'ec2':
            current_boto_list = get_all_ec2(
                account_number, region, cross_account_role)
        elif sqs_function == 'eks':
            current_boto_list = get_all_eks(
                account_number, region, cross_account_role)
        elif sqs_function == 'rds':
            current_boto_list = get_all_rds(
                account_number, region, cross_account_role)
        elif sqs_function == 'iam-roles':
            current_boto_list = get_all_iam_roles(
                account_number, 'us-east-1', cross_account_role)
        elif sqs_function == 'iam-users':
            current_boto_list = get_all_iam_users(
                account_number, 'us-east-1', cross_account_role)
        elif sqs_function == 'iam-attached-policys':
            current_boto_list = get_all_iam_attached_policys(
                account_number, 'us-east-1', cross_account_role)
        elif sqs_function == 'odcr':
            current_boto_list = get_all_odcr(
                account_number, region, cross_account_role)
        elif sqs_function == 'lightsail':
            current_boto_list = get_all_lightsail(
                account_number, region, cross_account_role)
        elif sqs_function == 'org':
            current_boto_list = get_organizations(
                account_number, region, cross_account_role)
        elif sqs_function == 'vpc':
            current_boto_list = get_all_vpc(
                account_number, region, cross_account_role)
        elif sqs_function == 'network-interfaces':
            current_boto_list = get_all_network_interfaces(
                account_number, region, cross_account_role)
        elif sqs_function == 'subnet':
            current_boto_list = get_all_subnets(
                account_number, region, cross_account_role)
        elif sqs_function == 'ri':
            current_boto_list = get_all_ris(
                account_number, region, cross_account_role)
        elif sqs_function == 's3-buckets':
            current_boto_list = get_all_s3_buckets(
                account_number, 'us-east-1', cross_account_role)
        elif sqs_function == 'org':
            current_boto_list = get_organizations(
                account_number, region, cross_account_role)
        else:
            print(f'Invalid function passed: {sqs_function}')
            raise ValueError(f'Invalid function passed: {sqs_function}')

        if sqs_function == 'org':
            dynamo_list = get_current_table_without_account(
                entry_type=sqs_function, region='us-east-1')
        else:
            dynamo_list = get_current_table(
                account_number=account_number, entry_type=sqs_function, region=region)

        # Deep copy instead of double dynamo read
        pop_dynamo = copy.deepcopy(dynamo_list)

        # remove Id key from dynamodb item and check if value has changed.
        compare_lists_and_update(
            boto_list=current_boto_list, dynamo_list=dynamo_list, pop_list=pop_dynamo)

    except ClientError as e:
        print(f'Error: {sqs_function} in {account_number} in {region} - {e}')
    except Exception as e:
        print(f'Error: {sqs_function} in {account_number} in {region} - {e}')


# Default Lambda
def lambda_handler(event, context):

    print(json.dumps(event))

    # message hasn't failed yet
    failed_message = False

    try:
        message = event['Records'][0]
    except KeyError:
        print('No messages on the queue!')

    try:
        message = event['Records'][0]
        print(json.dumps(message))
        sqs_function = message['messageAttributes']['Function']['stringValue']
        account_number = message['messageAttributes']['AccountNumber']['stringValue']
        region = message['messageAttributes']['Region']['stringValue']
        receipt_handle = event['Records'][0]['receiptHandle']

        print(f'sqs_function passed is: {sqs_function}')

        # Try run each function
        try:

            # Lambda logic
            compare_and_update_function(
                account_number, region, sqs_function, cross_account_role)

        except ClientError as e:
            print(
                f'Error: with {sqs_function}, in account {account_number}, in region {region} - {e}')
        except Exception as e:
            print(
                f'Error: with {sqs_function}, in account {account_number}, in region {region} - {e}')

    except ClientError as e:
        print(f'Error: on processing message, {e}')
        failed_message = True
    except Exception as e:
        print(f'Error: on processing message, {e}')
        failed_message = True

    # message must have passed, deleting
    if failed_message is False:
        client_sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )
