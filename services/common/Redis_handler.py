import redis
import base64
import json
from services.common.config import REDIS_HOST, REDIS_PORT
from datetime import datetime

class RedisHandler:
    def __init__(self):
        self.client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

    def get_query(self, redis_key: str) -> str:
        parts = redis_key.split(':')
        conversation_block_id = parts[0]
        conv_id = parts[1]
        try:
            data = self.client.hget(conversation_block_id, conv_id)
            if data:
                message_data = json.loads(data)
                return message_data.get('query', '')
            else:
                return f"No query found in Redis for conversation: {conv_id}"
        except Exception as e:
            return f"Error while fetching query from Redis: {str(e)}"
    
    def store_query(self, conv_id: str, query: str, *args, **kwargs) -> int:
        try:
            conversation_block_id = kwargs.get('conversation_block_id', -1)
            sender_id = kwargs.get('sender_id', -1)
            expiration = kwargs.get('expiration', None)
            pipeline = kwargs.get('pipeline', None)

            if isinstance(query, bytes):
                query = base64.b64encode(query).decode('utf-8')
            elif isinstance(query, (int, float)):
                query = str(query)

            message_data = {
                'query': str(query),
                'sender_id': str(sender_id),
                'timestamp': str(datetime.now().isoformat())
            }
            redis_key = f"{str(conversation_block_id)}:{conv_id}"
            
            if pipeline:
                if expiration:
                    pipeline.hset(conversation_block_id, conv_id, json.dumps(message_data))
                    pipeline.expire(conversation_block_id, time=expiration)
                else:
                    pipeline.hset(conversation_block_id, conv_id, json.dumps(message_data))
                return True
            else:
                if expiration:
                    self.client.hset(conversation_block_id, conv_id, json.dumps(message_data))
                    self.client.expire(conversation_block_id, time=expiration)
                else:
                    self.client.hset(conversation_block_id, conv_id, json.dumps(message_data))
                    return redis_key
                
        except Exception as e:
            print(f"Error in store_query: {str(e)}")
            raise

    def get_all_messages(self, conversation_block_id: str) -> dict:
        try:
            messages = self.client.hgetall(conversation_block_id)
            return {k: json.loads(v) for k, v in messages.items()}
        except Exception as e:
            print(f"Error fetching all messages: {str(e)}")
            return {}

    def delete_conversation_block(self, conversation_block_id: str) -> bool:
        try:
            return bool(self.client.delete(conversation_block_id))
        except Exception as e:
            print(f"Error deleting conversation block: {str(e)}")
            return False
        
    def conv_id_generator(self, conversation_block_id: str) -> str:
        try:
            messages = self.get_all_messages(conversation_block_id)
            if not messages:
                return "0"
            existing_ids = [int(msg_id) for msg_id in messages.keys() if msg_id.isdigit()]
            
            if not existing_ids:
                return "0"
            
            return str(max(existing_ids) + 1)
            
        except Exception as e:
            print(f"Error in conv_id_generator: {str(e)}")
            return "-1"

    def get_conversation_history(self, conversation_block_id: str) -> list:
        try:
            messages = self.get_all_messages(conversation_block_id)
            if not messages:
                return []
            history = []
            for conv_id, msg_data in messages.items():
                history.append({
                    'id': conv_id,
                    'content': msg_data['query'],
                    'sender': msg_data['sender_id'],
                    'timestamp': msg_data['timestamp']
                })
            return sorted(history, key=lambda x: int(x['id']) if x['id'].isdigit() else float('inf'))

        except Exception as e:
            print(f"Error in get_conversation_history: {str(e)}")
            return []
