import json
import os
import boto3
from botocore.exceptions import ClientError
from app import ChatHistoryHandler, WorkspaceHandler

def lambda_handler(event, context):
    try:
        workspace_id = event.get('workspace_id', '1')
        request_type = event.get('type', 'chat')
        
        # 创建处理器实例
        chat_handler = ChatHistoryHandler()
        workspace_handler = WorkspaceHandler()
        
        # 获取并打印聊天历史
        chat_history = chat_handler.get_chat_history(workspace_id)
        print("Chat History:", json.dumps(chat_history, indent=2))
        
        # 获取并打印工作区数据
        workspace_data = workspace_handler.get_workspace_data(workspace_id)
        print("Workspace Data:", json.dumps(workspace_data, indent=2))
        
        # 根据请求类型返回相应数据
        if request_type == 'chat':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps(chat_history)
            }
            
        elif request_type == 'workspace':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps(workspace_data)
            }
        
    except ClientError as e:
        error_message = f"Error loading data: {str(e)}"
        print("Error:", error_message)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'error': error_message
            })
        }
