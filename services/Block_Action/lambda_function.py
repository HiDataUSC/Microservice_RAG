import json
import os
import boto3
from botocore.exceptions import ClientError
from conversation_block import ConversationBlock

def lambda_handler(event, context):
    try:
        action_type = event.get('action_type')
        workspace_id = event.get('workspace_id')
        block_id = event.get('block_id')
        
        if not all([action_type, workspace_id, block_id]):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps('action_type, workspace_id and block_id are required')
            }
        
        conversation_block = ConversationBlock()
        
        if action_type == 'delete':
            result = conversation_block.delete_conversation(workspace_id, block_id)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps(f'Unknown action type: {action_type}')
            }
            
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps(f"Error: {str(e)}")
        } 