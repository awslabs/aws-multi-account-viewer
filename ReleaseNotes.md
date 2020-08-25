0.2.0.dev0 2020-xx-xx
=====================
1.  Added [Front-End/cloudformation/frontend_template.yaml](Front-End/cloudformation/frontend_template.yaml) 
    for deploying the frontend React app with S3 static hosting, CloudFront and OAI.
2.  Updated [images/AWS-Multi-Account-Overview.png](images/AWS-Multi-Account-Overview.png) to include CloudFront and
    private S3 static hosting.
3.  Added [Front-End/.env](Front-End/.env) and updated [Front-End/src/App.js](Front-End/src/App.js) to use .env.
4.  Added some helper scripts [scripts/](scripts/) to do the build and deployment.
5.  Fixed the `scan_table` and `query_table` functions in 
    [Back-End/lambdas/list_table.py](Back-End/lambdas/list_table.py) - 
    `data` is a list and should use `extend` not `update`, and both functions should return `data`.
6.  Redefined the primary key `Id` to use `ARN` or `Instance Id` of a resource instead of UUID, as `ARN` and
    `Instance Id` can uniquely identify a resource.
7.  Reimplemented the `compare_lists_and_update` function in 
    [Back-End/lambdas/receive_sqs_message.py](Back-End/lambdas/receive_sqs_message.py). The original approach was
    unable to avoid duplication as it compared the list object as a whole (without UUID) - duplicate entries 
    occurred when a field was changed  (e.g. codesize, state), and when multiple calls to update the same EntryType
    around the same time (due to eventually consistency nature of DynamoDB).
8.  Fixed the `get_current_table` and `get_current_table_without_account` functions in
    [Back-End/lambdas/receive_sqs_message.py](Back-End/lambdas/receive_sqs_message.py) - original code did not
    handle pagination resulting not retrieving all existing entries from the DynamoDB table.
9.  Fixed the `get_all_network_interfaces` function in
    [Back-End/lambdas/receive_sqs_message.py](Back-End/lambdas/receive_sqs_message.py) - original code retrieved
    only primary private/public IPs; updated to return also non primary IPs and added new field `Primary`.
10. Updated the `get_all_network_interfaces` function in
    [Back-End/lambdas/receive_sqs_message.py](Back-End/lambdas/receive_sqs_message.py) to include `SubnetId`,
    `VpcId` and `CidrBlock` to support querying which account/VPC/Subnet a given IP is located at within a single tab.
    
