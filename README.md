# aws-opensearch-dynamodb-stream

This repository consists of lambda function code in python 3.8 that enables you to stream dynamodb data to AWS Opensearch domain which is deployed within a VPC.

## Things to do

1. Add four environment variables to the lambda function.
    1. ES_HOST - OpenSearch domain endpoint host
    2. ES_INDEX - OpenSearch index name
    3. DB_HASH_KEY - DynamoDB Hash key attribute name
    4. DB_SORT_KEY - DynamoDB Sort key attribute name
2. Add a new role with the policy (use the contents of the stream_lambda_policy.json) and attach it as the execution role of the lambda. Replace the <accountId> with actual account id within the file.
3. The zip file opensearch_dynamodb_stream_lambda.zip contains the lambda function along with the dependant python 3.8 packages which can be uploaded to the lambda function code. If you are using a different python version, please use the corresponding packages.
