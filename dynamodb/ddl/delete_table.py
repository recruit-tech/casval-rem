from __future__ import print_function
import boto3
import os

dynamodb = boto3.resource(
    'dynamodb',
    os.getenv("DYNAMO_REGION", "ap-northeast-1")
)

if __name__ == '__main__':

    table = dynamodb.Table('Audit')
    table.delete()
