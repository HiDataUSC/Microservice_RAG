import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

class ConversationBlock:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(os.environ['DB_TABLE_NAME'])
    
    def delete_conversation(self, workspace_id: str, block_id: str) -> dict:
        """
        删除指定工作区和块ID的所有对话记录
        """
        try:
            # 查询该 block 的所有对话
            response = self.table.query(
                KeyConditionExpression=Key('workspace_id').eq(workspace_id) & 
                                     Key('sort_key').begins_with(f"{workspace_id}#{block_id}#")
            )
            
            # 批量删除所有对话记录
            with self.table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(
                        Key={
                            'workspace_id': item['workspace_id'],
                            'sort_key': item['sort_key']
                        }
                    )
            
            return {
                'message': f'Successfully deleted all conversations for block {block_id}',
                'deleted_count': len(response.get('Items', []))
            }
            
        except ClientError as e:
            raise Exception(f"Error deleting conversations: {str(e)}") 