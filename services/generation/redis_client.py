from services.common.Redis_handler import RedisHandler

class RedisClient(RedisHandler):
    def __init__(self):
        super().__init__()

    def get_query(self, redis_key: str) -> str:
        return super().get_query(redis_key=redis_key)
    
    def store_query(self, query, **kwargs):
        conversation_block_id = kwargs.get('conversation_block_id', -1)
        conv_id = self.conv_id_generator(conversation_block_id)
        return super().store_query(conv_id, query, **kwargs)
    
    def conv_id_generator(self, conversation_block_id: str) -> str:
        return super().conv_id_generator(conversation_block_id)
