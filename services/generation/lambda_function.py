import json
from services.generation.app import Generation

def lambda_handler(event, context):
    # 从事件中提取 query
    query = event.get('query', '')
    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps('Query is required')
        }
    
    # 初始化 Generation 类
    generation = Generation(mode='RAG')  # 或 'GPT'，根据需要选择模式
    
    # 生成答案
    answer = generation.generate_answer(redis_key=query)
    
    # 返回结果
    return {
        'statusCode': 200,
        'body': json.dumps(answer)
    } 