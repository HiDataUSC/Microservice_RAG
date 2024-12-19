import json
import boto3
from app import Generation, ConversationHistory, DynamoDBHandler
from shared import create_conversation_item

def lambda_handler(event, context):
    query = event.get('query', '')
    workspace_id = event.get('workspace_id', '1')
    block_id = event.get('block_id', 'default_block')
    
    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps('Query is required')
        }
    
    conversation_history = ConversationHistory()
    history = conversation_history.get_history(workspace_id, block_id)
    conversation_id = conversation_history.get_next_conversation_id(workspace_id, block_id)
    
    generation = Generation()
    answer = generation.generate_answer(query=query, history=history)
    
    messages = generation.create_messages(query, answer)
    metadata = generation.create_metadata()
    
    conversation_item = create_conversation_item(workspace_id, block_id, conversation_id, 'gpt-4', messages, metadata)
    
    db_handler = DynamoDBHandler()
    save_response = db_handler.save_to_dynamodb(conversation_item)
    
    return {
        'statusCode': 200,
        'body': answer
    }