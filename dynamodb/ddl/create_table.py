import boto3
import os

dynamodb = boto3.resource(
    'dynamodb',
    os.getenv("DYNAMO_REGION", "ap-northeast-1")
)


table = dynamodb.create_table(
    TableName='Audit',
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'status',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'updated_at',
            'AttributeType': 'S'
        },

    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'UpdatedAtIndex',
            'KeySchema': [
                {
                    'AttributeName': 'status',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'updated_at',
                    'KeyType': 'RANGE'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
)

print("Table status(Audit):", table.table_status)
