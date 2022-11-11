import boto3
import os

from dynamodb_json import json_util as json

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
from elasticsearch import helpers

HOST = os.environ.get('ES_HOST')
INDEX = os.environ.get('ES_INDEX')
DB_HASH_KEY = os.environ.get('DB_HASH_KEY')
DB_SORT_KEY = os.environ.get('DB_SORT_KEY')

def get_es():

    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()
    credentials = session.get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    session_token = credentials.token

    awsauth = AWSRequestsAuth(
        aws_access_key=access_key,
        aws_secret_access_key=secret_key,
        aws_token=session_token,
        aws_host=HOST,
        aws_region=session.region_name,
        aws_service='es'
    )

    return Elasticsearch(
        hosts=[{'host': HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

def pushBatch(actions):
    elasticsearch = get_es()
    print('Pushing batch of: ' + str(len(actions)) + ' to ES')
    (success, failed) = helpers.bulk(elasticsearch, actions, stats_only=True)
    print('Batch successfully pushed to elasticsearch')


def lambda_handler(event, context):

    eventTypes = ['INSERT', 'MODIFY', 'REMOVE']
    records = event['Records']
    actions = []
    ignoredRecordCount = 0
    for record in records:
        if record['eventName'] in eventTypes:
            action = json.loads(record['dynamodb']['OldImage']) \
                if record['eventName'] == 'REMOVE' \
                else json.loads(record['dynamodb']['NewImage'])
            actions.append(
                {
                    '_index': INDEX,
                    '_type': '_doc',
                    '_id': action[DB_HASH_KEY]+':'+action[DB_SORT_KEY],
                    '_source': action,
                    '_op_type': 'delete' if record['eventName'] == 'REMOVE'
                    else 'index'
                }
            )
        else:
            ignoredRecordCount += 1
            print(record)
        if len(actions) == 50:
            pushBatch(actions)
            actions = []

    if len(actions) > 0:
        pushBatch(actions)
    print('Invalid Event records ignored: ' + str(ignoredRecordCount))
