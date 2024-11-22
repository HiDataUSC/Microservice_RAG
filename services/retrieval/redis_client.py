from services.common.Redis_handler import RedisHandler

class RedisClient(RedisHandler):
    def __init__(self):
        super().__init__()

    def store_query(self, query, **kwargs):
        conversation_block_id = kwargs.get('conversation_block_id', -1)
        conv_id = self.conv_id_generator(conversation_block_id)
        return super().store_query(conv_id, query, **kwargs)
    
    def conv_id_generator(self, conversation_block_id: str) -> str:
        return super().conv_id_generator(conversation_block_id)
