0.2.0.dev0 2020-xx-xx
=====================
1. Added [cloudformation/backend_template.yaml](cloudformation/backend_template.yaml), an updated version of 
  [Back-End/cloudformation/MainTemplate_template.yaml](Back-End/cloudformation/MainTemplate_template.yaml).
2. Added [cloudformation/cognito_template.yaml](cloudformation/cognito_template.yaml) for deploying the Cognito
  components separately.
3. Added [cloudformation/frontend_template.yaml](cloudformation/frontend_template.yaml) for deploying the frontend
  React app with S3 static hosting, CloudFront and OAI.
4. Updated [images/AWS-Multi-Account-Overview.png](images/AWS-Multi-Account-Overview.png) to include CloudFront and
  private S3 static hosting.
5. Added [Front-End/.env](Front-End/.env)
6. Updated [Front-End/src/App.js](Front-End/src/App.js) to use .env.
7. Added [scripts/build_frontend.sh](scripts/build_frontend.sh)
8. Added [scripts/deploy_lambda.sh](scripts/deploy_lambda.sh)
9. Fixed the `scan_table` and `query_table` functions in 
  [Back-End/lambdas/list_table.py](Back-End/lambdas/list_table.py) - 
  `data` is a list and should use `extend` not `update`, and both functions should return `data`.
9. Redefined the primary key `Id` to use `ARN` or `Instance Id` of a resource instead of UUID, as `ARN` and
   `Instance Id` can uniquely identify a resource.
10. Reimplemented the `compare_lists_and_update` function in 
    [Back-End/lambdas/receive_sqs_message.py](Back-End/lambdas/receive_sqs_message.py). The original approach was
    unable to avoid duplication as it compared the list object as a whole (without UUID) - duplicate entries 
    occurred when a field was changed  (e.g. codesize, state), and when multiple calls to update the same EntryType
    around the same time (due to eventually consistency nature of DynamoDB).
11. Updated [Front-End/src/components/Navigation.js](Front-End/src/components/Navigation.js) to fix the label of
    "All Network Interfaces".
