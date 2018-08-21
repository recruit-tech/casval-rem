import os
import sys

import boto3

dynamodb = boto3.resource(
    'dynamodb',
    os.getenv("DYNAMO_REGION", "ap-northeast-1")
)

table = dynamodb.Table('Audit')
if __name__ == '__main__':
    try:
        with table.batch_writer() as batch:
            for i in range(10):
                batch.put_item(
                    Item={
                        "id": "3cd708cefd58401f9d43ff953f06346" + str(i),
                        "name": "コーポレートサイト",
                        "contacts": [
                            {
                                "name": "nishimunea",
                                "email": "nishimunea@example.jp"
                            }
                        ],
                        "scans": [
                            "21d6cd7b33e84fbf9a2898f4ea7f90cc"
                        ],
                        "password": "7a020f4e38f8b88a5103f732"
                                    "6d59c53317a18d53f4ff1aab"
                                    "66eacb27052c2050",
                        "status": "unsubmitted",
                        "rejected_reason": "深刻な脆弱性が修正されていません",
                        "restricted_by": {
                            "ip": True,
                            "password": False
                        },
                        "created_at": "2018-10-" + str(i + 1) + " 23:59:59",
                        "updated_at": "2018-10-" + str(i + 1) + " 23:59:59",
                    }
                )

    except Exception as e:
        print(e)
        print("Sequence table init data put error")
        sys.exit()

    print("Sequence table init data put success")
    print(table.scan())
