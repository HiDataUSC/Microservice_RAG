import json
import os
import boto3
from botocore.exceptions import ClientError
from conversation_block import ConversationBlock

def get_block_handler(block_type: str):
    """
    根据 block_type 返回对应的处理类实例
    """
    handlers = {
        'conversation': ConversationBlock(),
        # 未来可以添加其他类型的 handler
        # 'llm': LLMBlock(),
        # 'code': CodeBlock(),
        # 'knowledge': KnowledgeBlock(),
    }
    
    return handlers.get(block_type)

def lambda_handler(event, context):
    try:
        # 获取必要参数
        action_type = event.get('action_type')
        workspace_id = event.get('workspace_id')
        block_id = event.get('block_id')
        block_type = event.get('block_type')
        
        # 验证必要参数
        if not all([action_type, workspace_id, block_id, block_type]):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps('action_type, workspace_id, block_id and block_type are required')
            }
        
        # 获取对应的处理器
        block_handler = get_block_handler(block_type)
        if not block_handler:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps(f'Unsupported block type: {block_type}')
            }
        
        # 执行对应的操作
        if action_type == 'delete':
            result = block_handler.delete_conversation(workspace_id, block_id)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
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