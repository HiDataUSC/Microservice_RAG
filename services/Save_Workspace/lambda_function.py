import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime
from decimal import Decimal
import uuid

def convert_floats_to_decimals(obj):
    """递归地将对象中的浮点数转换为 Decimal"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(v) for v in obj]
    return obj

def get_next_project_id(table, workspace_id):
    """获取下一个可用的项目ID"""
    response = table.query(
        KeyConditionExpression=Key('workspace_id').eq(workspace_id)
    )
    
    # 找到当前最大的项目ID
    max_id = 0
    for item in response.get('Items', []):
        try:
            current_id = int(item['project_id'].split('-')[-1])
            max_id = max(max_id, current_id)
        except (ValueError, KeyError):
            continue
    
    # 返回下一个ID
    return f"project-{max_id + 1}"

def lambda_handler(event, context):
    try:
        workspace_id = event.get('workspace_id')
        project_id = event.get('project_id')
        flowchart_data = event.get('flowchart_data')
        
        if not workspace_id or not flowchart_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps('workspace_id and flowchart_data are required')
            }
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['WORKSPACE_TABLE_NAME'])
        
        # 如果没有提供 project_id，生成一个新的
        if not project_id:
            project_id = get_next_project_id(table, workspace_id)
        
        # 转换所有浮点数为 Decimal
        flowchart_data = convert_floats_to_decimals(flowchart_data)
        
        # 使用复合键：workspace_id#project_id
        composite_id = f"{workspace_id}#{project_id}"
        
        # 保存工作区数据
        item = {
            'workspace_id': workspace_id,
            'sort_key': composite_id,
            'project_id': project_id,
            'flowchart_data': flowchart_data,
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'message': 'Project data saved successfully',
                'project_id': project_id
            })
        }
        
    except ClientError as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps(f"Error saving project: {str(e)}")
        } 