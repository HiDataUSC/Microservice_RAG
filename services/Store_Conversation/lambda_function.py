import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DB_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # 直接将 event 作为 item 存储到 DynamoDB
        table.put_item(Item=event)
        return {
            'statusCode': 200,
            'body': json.dumps('Data saved successfully')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error saving to DynamoDB: {e.response['Error']['Message']}")
        }
