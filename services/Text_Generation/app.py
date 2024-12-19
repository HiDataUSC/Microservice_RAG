from llm_handler import LLMHandler
from datetime import datetime
import uuid
import boto3
import os
from langchain_core.messages import HumanMessage, AIMessage
from botocore.exceptions import ClientError
import json

class DynamoDBHandler:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(os.environ['DB_TABLE_NAME'])
    
    def save_to_dynamodb(self, item: dict) -> dict:
        try:
            self.table.put_item(Item=item)
            return {
                'statusCode': 200,
                'body': json.dumps('Data saved successfully')
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error saving to DynamoDB: {e.response['Error']['Message']}")
            }

class ConversationHistory:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(os.environ['DB_TABLE_NAME'])
    
    def get_history(self, workspace_id: str, block_id: str) -> list:
        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('workspace_id').eq(workspace_id) & 
                                   boto3.dynamodb.conditions.Key('sort_key').begins_with(f"{workspace_id}#{block_id}#")
        )
        
        history = []
        for item in response.get('Items', []):
            if 'messages' not in item:
                continue
                
            messages = item.get('messages', [])
            if not isinstance(messages, list):
                continue
                
            for message in messages:
                try:
                    content = message.get('content', '')
                    role = message.get('role', '')
                    if role == 'user':
                        history.append(HumanMessage(content=content))
                    else:
                        history.append(AIMessage(content=content))
                except Exception as e:
                    continue
        
        return history
    
    def get_next_conversation_id(self, workspace_id: str, block_id: str) -> int:
        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('workspace_id').eq(workspace_id) & 
                                   boto3.dynamodb.conditions.Key('sort_key').begins_with(f"{workspace_id}#{block_id}#")
        )
        
        max_conversation_id = -1
        for item in response.get('Items', []):
            conversation_id = int(item['conversation_id'])
            if conversation_id > max_conversation_id:
                max_conversation_id = conversation_id

        return max_conversation_id + 1

class Generation:
    def __init__(self):
        self.llm_handler = LLMHandler()

    def generate_answer(self, query: str, history: list) -> str:
        """
        Generate an answer based on the query and conversation history.
        :param query: User's query
        :param history: List of previous conversation messages
        :return: Generated answer as a string
        """
        answer = self.llm_handler.generate_answer(question=query, history=history)
        return answer

    def create_messages(self, query: str, answer: str):
        """
        Create messages for the conversation.
        :param query: User's query
        :param answer: Generated answer
        :return: List of message dictionaries
        """
        return [
            {
                'message_id': str(uuid.uuid4()),
                'role': 'user',
                'content': query,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            {
                'message_id': str(uuid.uuid4()),
                'role': 'assistant',
                'content': answer,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        ]

    def create_metadata(self):
        """
        Create metadata for the conversation.
        :return: Metadata dictionary
        """
        return {
            'language': 'en',
            'platform': 'web',
            'custom_tags': ['conversation_summary', 'user_feedback']
        }
