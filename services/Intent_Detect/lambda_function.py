import json
from app import IntentDetector
from intent_handlers import IntentHandlerFactory

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
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps('Query is required')
            }
        
        # 1. 检测意图
        detector = IntentDetector()
        intent_result = detector.detect(
            text=query,
            workspace_id=workspace_id,
            block_id=block_id,
            connections=connections
        )
        
        # 2. 获取对应的处理器并处理
        handler = IntentHandlerFactory.get_handler(intent_result['intent_id'])
        handler_result = handler.handle(body)
        
        # 3. 直接返回处理结果
        return handler_result
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Processing error: {str(e)}'
            })
        } 