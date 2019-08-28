<h1 align="center">
<img src="https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/frontpage.png"></a>
</h1>

## Overview

Serverless app designed for any customer with two or more accounts to view resources across accounts/regions in simple single pane of glass website. It's split into 2 customizable parts:

- Back-End (Cloudformation templates and Python Lambads)
- Front-End (React with Amplify)

some of the current working features are:

- All AWS Accounts in Organizations
- All EC2/ODCR/RIs
- All RDS Instances
- All IAM Users/Roles/Policys
- All Lambdas
- All VPCs/Subnets
- All On Demand Capacity Reservations

## On this Page
- [Architecture](#architecture)
- [Screen Shots](#Screenshots)
- [Requirements](#Requirements)
- [Install Overview](#install-overview) 
- [Deploying the Solution](#deploying-the-solution)
- [Adding-New-Services](#adding-new-services)
- [Troubleshooting](#Troubleshooting)
- [License](#license)


## Architecture

![Architecture](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/AWS-Multi-Account-Overview.png)

## Screenshots

### Required Authentication through Cognito

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sample-login.png)

### EC2 Sample

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sample-ec2.png)

### Iam Attached Roles Sample

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sample-iam.png)

### Organizations Sample

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sample-org.png)


## Requirements

- [Python 3.7](https://www.python.org/downloads/)
- [Node.js 8.10+](https://nodejs.org/en/)
- [Yarn](https://yarnpkg.com/en/)
- At least 2 AWS accounts.

## Install Overview

Administrator account is the account you will use to access all sub accounts and where you will store everything.
SubAccounts only requires the SubAccountAccess template to be created.

- Clone repo
- Run Cloudformation script in your sub accounts (SubAccountAccess.yaml)
- Run Cloudformation script in your main account (MainTemplate.yaml)
- Run React App.

## Deploying the Solution

#### Sub Accounts

- Note the Account number for your Administrator Account and put it into the SubAccountAccess template.
- Edit the __SubAccountAccess.yaml__ with your Administrator Account Number (this account number will be your Administrator account that will have access to view all the sub accounts from)
![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sub-account.png)
- Save and Run the __SubAccountAccess.yaml__ in all your sub accounts you want to view. (I recommend using [StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html) if you have them enabled otherwise manual is fine)

#### Administrator Account

- Create a new S3 bucket to store the lambda zip files

```bash
aws s3 mb s3://your-unique-bucket-name --region ap-southeast-2
```
- Package up all the lambdas into one zip file (e.g __functions.zip__): see example below or doco [here](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) 

- The only external python modules: boto3

```bash
cd ~/Back-End/lambdas
python3.7 -m venv .venv
source .venv/bin/activate
cd build
pip install -r ../requirements.txt --target .
zip -r9 ../functions.zip .
deactivate
cd ../
zip -g functions.zip list_table.py receive_sqs_message.py send_sqs_message.py
```

- Copy the functions.zip file you just packaged into the s3 bucket you created earlier.

```bash
aws s3 cp functions.zip s3://your-unique-bucket-name
```
- Update all the parameters to match your config/accounts/bucket in MainTemplate.yaml
- Deploy the cloudformation template in the admin account once you have updated the paramaters
- Once the cloudformation has completed copy the details in the outputs:
    - __ApiGateWayEndPoint__
    - __UserPoolId__
    - __userPoolWebClientId__

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/cloudformation-outputs.png)

- Paste the outputs into ~/Front-End/src/App.js

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/cognito.png)

- Create a user account for the Cognito User Pool (sign up is disabled, so users have to be created manually)
- Cognito > User Pools > {YourStackName} > Users and groups > Create User.
- Now navigate to Front-End and Install dependencies

```bash
cd ~/Front-End/
yarn
```
![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/yarn-2.png)

- Start React Page

```bash
yarn start
```
![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/yarn.png)

- You should now see a login page from React

![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/login-complete.png)

- Log in with the user you created earlier.
- You now have a local version up and running, to move to production you can simply build it and move it into a s3 public bucket. (not covered in this project but you can see examples online: __details here__)


## Adding New Services

To add a new services you need to updating 2 sqs lambdas and creating a new page in the Front-End. 
Example coming soon.

## Troubleshooting

### No data is being populated on the web site?

- Check SQS to make sure the messages are going through to lambda
- If theres lots of messages in the queue then theres an issue with the lambda or dynamoDB is throttling the requests.

### Lambda Logs Overview?

- You can check all three lambdas logs easy in Cloudwatch Insights:
![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sample-insights.png)

### Lambda Logs Error & Exceptions:

Copy and paste query below to only see Errors & Exceptions:
(this example is showing throttle requests on DynamoDB because its set too low):

```bash
fields @message 
| filter @message like /error/ or @message like /exception/
| limit 50
```
![](https://aws-multi-account-viewer-site.s3-ap-southeast-2.amazonaws.com/sample-exception.png)

### Organizations tab is empty?
- Organizations isn't part of the cron job that normally goes, You need to manually refresh it.
- Go to Refresh Checks > Organizations > Send to SQS
- You should now see Organizations populated.

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.