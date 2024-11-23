from services.common.Redis_handler import RedisHandler

class RedisClient(RedisHandler):
    def __init__(self):
        super().__init__()

    def store_query(self, query, conversation_block_id, **kwargs):
        conv_id = self.conv_id_generator(conversation_block_id)
        return super().store_query(conv_id, query, conversation_block_id, **kwargs)
    
    def conv_id_generator(self, conversation_block_id: str) -> str:
        return super().conv_id_generator(conversation_block_id)
