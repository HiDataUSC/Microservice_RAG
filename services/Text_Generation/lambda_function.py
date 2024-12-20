import json
import boto3
from app import Generation, ConversationHistory, DynamoDBHandler
from shared import create_conversation_item

def lambda_handler(event, context):
    """
    AWS Lambda handler for text generation requests.
    Processes incoming requests, generates responses using LLM, and stores conversation history.
    
    Args:
        event: AWS Lambda event object containing request data
        context: AWS Lambda context object
        
    Returns:
        dict: Response containing generated answer or error message
    """
    # Extract request parameters
    query = event.get('query', '')
    workspace_id = event.get('workspace_id', '1')
    block_id = event.get('block_id', 'default_block')
    connections = event.get('connections', [])
    
    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps('Query is required')
        }
    
    conversation_history = ConversationHistory()
    
    # Get current conversation history
    current_history = conversation_history.get_history(workspace_id, block_id)
    
    # Collect external knowledge sources
    external_sources = []
    
    # Process connected nodes
    for connection in connections:
        connected_block_id = connection.get('id')
        connected_block_type = connection.get('type')
        
        if connected_block_type == 'conversation':
            # Get conversation history from connected node as external source
            connected_history = conversation_history.get_history(workspace_id, connected_block_id)
            external_sources.append({
                'type': 'conversation_history',
                'content': connected_history,
                'source_id': connected_block_id
            })
        # Future extension point for other types
        # elif connected_block_type == 'knowledge':
        #     knowledge_content = knowledge_handler.get_knowledge(workspace_id, connected_block_id)
        #     external_sources.append({
        #         'type': 'knowledge_base',
        #         'content': knowledge_content,
        #         'source_id': connected_block_id
        #     })
    
    # Get next conversation ID for storage
    conversation_id = conversation_history.get_next_conversation_id(workspace_id, block_id)
    
    # Generate answer using LLM
    generation = Generation()
    answer = generation.generate_answer(
        query=query, 
        current_history=current_history,
        external_sources=external_sources
    )
    
    # Create conversation records
    messages = generation.create_messages(query, answer)
    metadata = generation.create_metadata()
    
    # Store conversation in database
    conversation_item = create_conversation_item(workspace_id, block_id, conversation_id, 'gpt-4', messages, metadata)
    
    db_handler = DynamoDBHandler()
    save_response = db_handler.save_to_dynamodb(conversation_item)
    
    return {
        'statusCode': 200,
        'body': answer
    }