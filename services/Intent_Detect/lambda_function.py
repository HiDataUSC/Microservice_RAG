import json
from app import IntentDetector

def lambda_handler(event, context):
    try:
        # 检查 event 是否已经是字典类型
        if isinstance(event, dict):
            body = event
        else:
            # 尝试解析 event body
            body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        # 获取输入参数
        query = body.get('query', '')
        workspace_id = body.get('workspace_id', '')
        block_id = body.get('block_id', '')
        connections = body.get('connections', [])
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Please provide input text'
                })
            }
        
        detector = IntentDetector()
        
        intent_result = detector.detect(
            text=query,
            workspace_id=workspace_id,
            block_id=block_id,
            connections=connections
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(intent_result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'processing error: {str(e)}'
            })
        } 