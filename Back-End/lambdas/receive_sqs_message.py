# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import os
import decimal
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

            lambda_arn = i['FunctionArn']
            lambda_name = i['FunctionName']

            # Try Get Tags
            try:
                lambda_tag = client_lambda.list_tags(Resource=lambda_arn)['Tags']
            except ClientError as e:
                lambda_tag = 'No Tags Exist'

            var_list.append(
                {
                    'EntryType': 'lambda',
                    'Region': str(region),
                    'FunctionName': str(lambda_name),
                    'Id': str(lambda_arn),
                    'Runtime': str(i['Runtime']),
                    'AccountNumber': str(account_number),
                    'Timeout': str(i['Timeout']),
                    'RoleName': str(iam_role),
                    'Handler': str(i['Handler']),
                    'CodeSize': int(i['CodeSize']),
                    'Link': str(f'https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{lambda_name}'),
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

            #Try Get Tags
            try:
                rds_tag = client_rds.list_tags_for_resource(ResourceName=instance)['TagList']
            except ClientError as e:
                rds_tag = 'No Tags Exist'

            var_list.append(
                {
                    'EntryType': 'rds',
                    'Region': str(region),
                    'AccountNumber': str(account_number),
                    'State': str(i['DBInstanceStatus']),
                    'Id': str(i['DBInstanceIdentifier']),
                    'DBInstanceClass': str(i['DBInstanceClass']),
                    'AllocatedStorage': int(i.get('AllocatedStorage', ' ')),
                    'PreferredBackupWindow': str(i.get('PreferredBackupWindow', ' ')),
                    'BackupRetentionPeriod': str(i.get('BackupRetentionPeriod', ' ')),
                    'PreferredMaintenanceWindow': str(i.get('PreferredMaintenanceWindow', ' ')),
                    'Link': str(f'https://{region}.console.aws.amazon.com/rds/home?region={region}#databases:'),
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

            var_list.append({
                'AccountNumber': str(account_number),
                'EntryType': str('eks'),
                'Region': str(region),
                'Name': str(eks_detail['name']),
                'Id': str(eks_detail['arn']),
                'Status': str(eks_detail['status']),
                'RoleArn': str(eks_detail.get('roleArn', ' ')),
                'Created': str(eks_detail['createdAt']),
                'VpcId': str(eks_detail['resourcesVpcConfig'].get('vpcId', ' ')),
                'PlatformVersion': str(eks_detail['platformVersion']),
                'Link': (f'https://{region}.console.aws.amazon.com/eks/home?region={region}#/clusters/{cluster_name}'),
                'K8 Version': str(eks_detail['version']),
                'Endpoint': str(eks_detail['endpoint']),
                'Tags': str(eks_detail.get('tags', 'No Tags Exist'))
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
            ec2_tags = i['Instances'][0].get('Tags', 'No Tags Exist')

            var_list.append(
                {
                    'EntryType': 'ec2',
                    'Id': str(i['Instances'][0]['InstanceId']),
                    'State': str(i['Instances'][0]['State']['Name']),
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'vCPU': int(vCPU),
                    'KeyName': str(i['Instances'][0].get('KeyName', ' ')),
                    'RoleName': str(iam_role),
                    'Link': str(f'https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:sort=instanceId'),
                    'PrivateIpAddress': str(i['Instances'][0].get('PrivateIpAddress', ' ')),
                    'PublicIpAddress': str(i['Instances'][0].get('PublicIpAddress', ' ')),
                    'InstancePlatform': str(i['Instances'][0].get('Platform', 'Linux/UNIX')),
                    'InstanceType': str(i['Instances'][0]['InstanceType']),
                    'Tags': str(ec2_tags)
                })

    return var_list


# Get ALB/NLB/ELB Function
def get_all_load_balancers(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_elb = create_boto_client(
        account_number, region, 'elb', cross_account_role)

    # ALB/NLB
    client_elbv2 = create_boto_client(
        account_number, region, 'elbv2', cross_account_role)

    # Page all elb's
    paginator = client_elb.get_paginator('describe_load_balancers')

    for page in paginator.paginate():
        for i in page['LoadBalancerDescriptions']:

            var_list.append(
                {
                    'EntryType': 'lb',
                    'LoadBalancerName': str(i['LoadBalancerName']),
                    'Id': str(i['DNSName']),
                    'Scheme': str(i['Scheme']),
                    'VPC': str(i['VPCId']),
                    'State': 'n/a',
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'AvailabilityZones': str(i['AvailabilityZones']),
                    'SecurityGroups': str(i['SecurityGroups']),
                    'Type': 'classic'
                })

    # Page all ALB/NLB
    paginator2 = client_elbv2.get_paginator('describe_load_balancers')

    for page in paginator2.paginate():
        for i in page['LoadBalancers']:

            var_list.append(
                {
                    'EntryType': 'lb',
                    'LoadBalancerName': str(i['LoadBalancerName']),
                    'Id': str(i['DNSName']),
                    'Scheme': str(i['Scheme']),
                    'State': str(i['State']['Code']),
                    'VPC': str(i['VpcId']),
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'AvailabilityZones': str(i['AvailabilityZones']),
                    'SecurityGroups': str(i.get('SecurityGroups', ' ')),
                    'Type': str(i['Type'])
                })

    return var_list


# Get EBS Volumes
def get_all_ebs(account_number, region, cross_account_role):
    
    # Init
    var_list = []

    # Use boto3 on source account
    client_ebs = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    # Page all elb's
    paginator = client_ebs.get_paginator('describe_volumes')

    for page in paginator.paginate():
        for i in page['Volumes']:

            var_list.append(
                {
                    'EntryType': 'ebs',
                    'Id': str(i['VolumeId']),
                    'State': str(i['State']),
                    'Size': str(i['Size']),
                    'VolumeType': str(i['VolumeType']),
                    'AccountNumber': str(account_number),
                    'Region': str(region),
                    'Tags': str(i.get('Tags', 'No Tag')),
                    'Encrypted': str(i['Encrypted']),
                    'SnapshotId': str(i['SnapshotId']),
                    'AvailabilityZone': str(i['AvailabilityZone']),
                    'CreateTime': str(i['CreateTime'])
                })

    return var_list


# Get IAM Roles Function
def get_all_iam_roles(account_number, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_iam = create_boto_client(
        account_number, 'us-east-1', 'iam', cross_account_role)

    # Page roles
    paginator = client_iam.get_paginator('list_roles')

    for page in paginator.paginate():
        for i in page['Roles']:

            role_name = i['RoleName']

            # Get Tags for Role
            try:
                print(f'Getting Tags for: {role_name}...')
                tags = client_iam.list_role_tags(RoleName=role_name)['Tags']
            except ClientError as e:
                tags = 'No Tags Exist'

            var_list.append(
                {
                    'Id': str(i['Arn']),
                    'EntryType': 'iam-roles',
                    'Region': 'us-east-1',
                    'AccountNumber': str(account_number),
                    'Link': str(f"https://console.aws.amazon.com/iam/home?region=us-east-1#/roles/{role_name}"),
                    'Tags': str(tags),
                    'RoleName': str(role_name),
                    'CreateDate': str(i['CreateDate'])
                })

    return var_list


# Get IAM Users Function
def get_all_iam_users(account_number, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_iam = create_boto_client(
        account_number, 'us-east-1', 'iam', cross_account_role)

    # Page users
    paginator = client_iam.get_paginator('list_users')

    for page in paginator.paginate():
        for i in page['Users']:

            username = i['UserName']

            # Get Tags for User
            try:
                print(f'Getting Tags for: {username}...')
                tags = client_iam.list_user_tags(UserName=username)['Tags']
            except ClientError as e:
                tags = 'No Tags Exist'

            var_list.append(
                {
                    'Id': str(i['Arn']),
                    'EntryType': 'iam-users',
                    'AccountNumber': str(account_number),
                    'Region': 'us-east-1',
                    'Link': str(f"https://console.aws.amazon.com/iam/home?region=us-east-1#/users/{username}"),
                    'UserName': str(username),
                    'Tags': str(tags),
                    'PasswordLastUsed': str(i.get('PasswordLastUsed', ' ')),
                    'CreateDate': str(i['CreateDate'])
                })

    return var_list


# Get IAM Users Function
def get_all_iam_attached_policys(account_number, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_iam = create_boto_client(
        account_number, 'us-east-1', 'iam', cross_account_role)

    # Page policys
    paginator = client_iam.get_paginator('list_policies')

    for page in paginator.paginate(OnlyAttached=True):
        for i in page['Policies']:
            var_list.append(
                {
                    'Id': str(i['Arn']),
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
                        'Id': str(i['CapacityReservationId']),
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
                    'Id': str(i['arn']),
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

                acc_number = i['Id']

                # Try Get Tags
                try:
                    org_tags = client_org.list_tags_for_resource(ResourceId=acc_number)['Tags']
                except ClientError as e:
                    org_tags = 'No Tags Exist'

                var_list.append(
                    {
                        'AccountNumber': str(acc_number),
                        'Id': str(i['Arn']),
                        'Region': 'us-east-1',
                        'EntryType': 'org',
                        'Name': str(i['Name']),
                        'Email': str(i['Email']),
                        'Status': str(i['Status']),
                        'JoinedMethod': str(i['JoinedMethod']),
                        'Tags': str(org_tags)
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
                    'Id': str(i['VpcId']),
                    'DhcpOptionsId': str(i['DhcpOptionsId']),
                    'InstanceTenancy': str(i['InstanceTenancy']),
                    'Link': str(f'https://{region}.console.aws.amazon.com/vpc/home?region={region}#vpcs:sort=VpcId'),
                    'Tags': str(i.get('Tags', 'No Tags Exist'))
                })

    return var_list


# Get All Network Interfaces Function
def get_all_network_interfaces(account_number, region, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_ec2 = create_boto_client(
        account_number, region, 'ec2', cross_account_role)

    retrieved_subnets = {}
    def get_subnet(subnet_id):
        try:
            if subnet_id and subnet_id not in retrieved_subnets:
                retrieved_subnets[subnet_id] = client_ec2.describe_subnets(SubnetIds=[subnet_id])['Subnets'][0]
            return retrieved_subnets[subnet_id]
        except:
            print(f"Unable to call describe_subnets for {subnet_id}")
        return {}

    # Page all vpc's
    paginator = client_ec2.get_paginator('describe_network_interfaces')

    for page in paginator.paginate():
        for i in page['NetworkInterfaces']:
            data = {
                'EntryType': 'network-interfaces',
                'PrivateIpAddress': str(i.get('PrivateIpAddress', ' ')),
                'PublicIp': str(i.get('Association', {}).get('PublicIp', ' ')),
                'AccountNumber': str(account_number),
                'Region': str(region),
                'Status': str(i.get('Status', ' ')),
                'Link': str(f"https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#NIC:sort=networkInterfaceId"),
                'AttStatus': str(i.get('Attachment', {}).get('Status', ' ')),
                'InterfaceType': str(i.get('InterfaceType', ' ')),
                'NetworkInterfaceId': str(i.get('NetworkInterfaceId', ' ')),
                'SubnetId': str(i.get('SubnetId', ' ')),
                'VpcId': str(i.get('VpcId', ' ')),
                'CidrBlock': str(get_subnet(i.get('SubnetId')).get('CidrBlock', ' ')),
                'Tags': str(i.get('TagSet', 'No Tags Exist')),
                'Description': str(i.get('Description', ' '))
            }

            for ip in i["PrivateIpAddresses"]:
                data.update({
                    'Id': f"{i['NetworkInterfaceId']}-{ip['PrivateIpAddress']}",
                    'PrivateIpAddress': ip['PrivateIpAddress'],
                    'PublicIp': ip.get('Association', {}).get('PublicIp', ' '),
                    'Primary': ip['Primary'],
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
                'Id': str(i['SubnetId']),
                'VpcId': str(i['VpcId']),
                'SubnetArn': str(i['SubnetArn']),
                'AvailableIpAddressCount': i['AvailableIpAddressCount'],
                'Tags': str(i.get('Tags', 'No Tags Exist'))
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
                    'Id': str(i['ReservedInstancesId']),
                    'Start': str(i['Start']),
                    'End': str(i['End']),
                    'InstanceTenancy': str(i['InstanceTenancy']),
                    'OfferingClass': str(i['OfferingClass'])
                })

    return var_list


# Get S3 Buckets # REGION FORCED TO US-EAST-1
def get_all_s3_buckets(account_number, cross_account_role):

    # Init
    var_list = []

    # Use boto3 on source account
    client_s3 = create_boto_client(
        account_number, 'us-east-1', 's3', cross_account_role)

    # No paginator for listing buckets
    # paginator = client_ec2.get_paginator('')
    result = client_s3.list_buckets()

    for i in result['Buckets']:
        bucket_name = i['Name']
        bucket_creation_date = i['CreationDate']
        bucket_region = ' '
        bucket_tag = ' '

        # Try Get Region
        try:
            print(f'Getting Region for bucket: {bucket_name}')
            bucket_region = client_s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        except ClientError as e:
            bucket_region = ' '

        #Try Get Tags
        try:
            print(f'Getting Tags for bucket: {bucket_name}')
            bucket_tag = client_s3.get_bucket_tagging(Bucket=bucket_name)['TagSet']
        except ClientError as e:
            bucket_tag = 'No Tags Exist'

        var_list.append(
            {
                'Id': str(bucket_name),
                'Link': str(f'https://s3.console.aws.amazon.com/s3/buckets/{bucket_name}/?region={bucket_region}&tab=overview'),
                'EntryType': 's3-buckets',
                'AccountNumber': str(account_number),
                'Region': str(bucket_region),
                'Tags': str(bucket_tag),
                'CreationDate': str(bucket_creation_date)
            })

    return var_list


# Get data sitting in DynamoDB
def get_current_table(entry_type, region=None, account_number=None):
    try:
        # Scan dynamo for all data
        params = {
            'IndexName': 'EntryType-index',
            'KeyConditionExpression': Key('EntryType').eq(entry_type),
        }
        
        if account_number is not None and region is not None:
            params['FilterExpression'] = Attr('AccountNumber').eq(account_number) & Attr('Region').eq(region)
        elif account_number is not None:
            params['FilterExpression'] = Attr('AccountNumber').eq(account_number)
        else:
            params['FilterExpression'] = Attr('Region').eq(region)
        
        response = table.query(**params)
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            params["ExclusiveStartKey"] = response['LastEvaluatedKey']
            response = table.query(**params)
            data.extend(response['Items'])
        
        return data
    
    except ClientError as e:
        print(f'Error: failed to query dynamodb table...{e}')
    except Exception as e:
        print(f'Error: failed to query dynamodb table...{e}')


# DynamoDB Create/Replace Item
def dynamo_put_item(dynamodb_item):

    try:

        # Put item
        response = table.put_item(Item=dynamodb_item)

        print(f'Successfully added/updated {dynamodb_item}')
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

        print(f'Successfully deleted {dynamodb_item}')
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
def compare_lists_and_update(boto_list, dynamo_list):
    current_ids = [item['Id'] for item in boto_list]
    existing_ids = [item['Id'] for item in dynamo_list]
    
    for existing_id in existing_ids:
        if existing_id not in current_ids:
            dynamo_delete_item(existing_id)
    
    for resource in boto_list:
        strip_empty_values = {k: v for k, v in resource.items() if v}
        dynamo_put_item(strip_empty_values)


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
        elif sqs_function == 'lb':
            current_boto_list = get_all_load_balancers(
                account_number, region, cross_account_role)
        elif sqs_function == 'ebs':
            current_boto_list = get_all_ebs(
                account_number, region, cross_account_role)
        elif sqs_function == 'eks':
            current_boto_list = get_all_eks(
                account_number, region, cross_account_role)
        elif sqs_function == 'rds':
            current_boto_list = get_all_rds(
                account_number, region, cross_account_role)
        elif sqs_function == 'iam-roles':
            current_boto_list = get_all_iam_roles(
                account_number, cross_account_role)
        elif sqs_function == 'iam-users':
            current_boto_list = get_all_iam_users(
                account_number, cross_account_role)
        elif sqs_function == 'iam-attached-policys':
            current_boto_list = get_all_iam_attached_policys(
                account_number, cross_account_role)
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
                account_number, cross_account_role)
        elif sqs_function == 'org':
            current_boto_list = get_organizations(
                account_number, region, cross_account_role)
        else:
            print(f'Invalid function passed: {sqs_function}')
            raise ValueError(f'Invalid function passed: {sqs_function}')

        if sqs_function == 'org':
            dynamo_list = get_current_table(entry_type=sqs_function, region='us-east-1')
        # Don't search regions for global API's
        elif sqs_function in ['s3-buckets', 'iam-roles', 'iam-users', 'iam-attached-policys']:
            dynamo_list = get_current_table(entry_type=sqs_function, account_number=account_number)
        else:
            dynamo_list = get_current_table(entry_type=sqs_function, region=region, account_number=account_number)
        
        print(f'Comparing: {sqs_function} {account_number} {region} current={len(current_boto_list)} prev={len(dynamo_list)}')
        
        compare_lists_and_update(boto_list=current_boto_list, dynamo_list=dynamo_list)

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
