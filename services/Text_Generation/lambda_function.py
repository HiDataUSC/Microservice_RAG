import json
from app import Generation

def lambda_handler(event, context):
    query = event.get('query', '')
    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps('Query is required')
        }
    
    generation = Generation()
    
    answer = generation.generate_answer(query=query)
    
    return {
        'statusCode': 200,
        'body': json.dumps(answer)
    } 