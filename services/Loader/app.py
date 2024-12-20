import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

class DynamoDBMixin:
    """提供 DynamoDB 基本功能的 Mixin 类"""
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def get_table(self, table_name):
        return self.dynamodb.Table(table_name)

class ChatHistoryHandler(DynamoDBMixin):
    """处理聊天历史记录的类"""
    
    def __init__(self):
        super().__init__()
        self.table = self.get_table(os.environ['DB_TABLE_NAME'])
    
    def get_chat_history(self, workspace_id: str) -> list:
        """获取指定工作区的聊天历史"""
        response = self.table.query(
            KeyConditionExpression=Key('workspace_id').eq(workspace_id)
        )
        
        return self._format_chat_history(response.get('Items', []))
    
    def _format_chat_history(self, items: list) -> list:
        """格式化聊天历史记录"""
        block_chats = {}
        for item in items:
            block_id = item['block_id']
            conversation_id = int(item['conversation_id'])
            messages = item.get('messages', [])
            
            if block_id not in block_chats:
                block_chats[block_id] = []
            
            for message in messages:
                block_chats[block_id].append({
                    'id': conversation_id,
                    'text': message.get('content', ''),
                    'isUser': message.get('role', '') == 'user',
                    'timestamp': message.get('timestamp', '')
                })
        
        result = [
            {
                'blockId': block_id,
                'messages': sorted(messages, key=lambda x: x['id'])
            }
            for block_id, messages in block_chats.items()
        ]
        
        return result

class WorkspaceHandler(DynamoDBMixin):
    """处理工作区数据的类"""
    
    def __init__(self):
        super().__init__()
        self.table = self.get_table(os.environ['WORKSPACE_TABLE_NAME'])
    
    def get_workspace_data(self, workspace_id: str) -> dict:
        """获取工作区的所有数据"""
        response = self.table.query(
            KeyConditionExpression=Key('workspace_id').eq(workspace_id)
        )
        
        # 直接返回原始数据，只做必要的 Decimal 转换
        workspace_data = {
            'projects': []
        }
        
        for item in response.get('Items', []):
            if 'project_id' in item and 'flowchart_data' in item:
                project = {
                    'id': item['project_id'],
                    'flowchartData': self._decimal_to_float(item['flowchart_data'])
                }
                workspace_data['projects'].append(project)
        
        return workspace_data
    
    def _decimal_to_float(self, obj):
        """将 Decimal 转换回 float"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._decimal_to_float(v) for v in obj]
        return obj