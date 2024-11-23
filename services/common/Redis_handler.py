import redis
import base64
import json
from typing import Optional, Dict, List, Any, Union, get_type_hints
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from services.common.config import REDIS_HOST, REDIS_PORT

@dataclass
class Message:
    """Data class representing the structure of a message.
    Contains both required and optional fields for message storage and retrieval.
    
    Required Fields:
        - query: The main content of the message
        
    Optional Fields:
        - sender_id: Identifier for the message sender
        - timestamp: Time when the message was created
    """
    query: str
    sender_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing of message fields.
        - Sets default timestamp if none provided
        - Ensures proper string formatting for all fields
        - Handles base64 encoding for binary query data
        """
        # Set default timestamp if not provided
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        
        # Ensure query is properly formatted as string
        if isinstance(self.query, bytes):
            self.query = base64.b64encode(self.query).decode('utf-8')
        self.query = str(self.query)
        
        # Ensure sender_id is string type if provided
        if self.sender_id is not None:
            self.sender_id = str(self.sender_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts message object to dictionary format.
        Only includes non-None values to minimize storage space.
        
        Returns:
            Dict containing message data with non-None values
        """
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def get_optional_fields(cls) -> List[str]:
        """Retrieves names of all optional fields in the Message class using reflection.
        
        Criteria for optional fields:
        - Not the required 'query' field
        - Has None as default value
        - Marked as Optional in type hints
        
        Returns:
            List of optional field names
        """
        type_hints = get_type_hints(cls)
        return [
            field.name for field in fields(cls)
            if (
                field.name != 'query'  # Exclude required field
                and field.default is None  # Only fields with None default
                and 'Optional' in str(type_hints.get(field.name, ''))  # Must be Optional type
            )
        ]
    
    @classmethod
    def to_history_format(cls, conv_id: str, msg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Converts message data to history record format.
        
        Args:
            conv_id: Conversation identifier
            msg_data: Raw message data dictionary
            
        Returns:
            Formatted history record with standard and optional fields
        """
        # Base fields required in all history records
        history_dict = {
            'id': conv_id,
            'content': msg_data['query']
        }
        
        # Add any available optional fields
        for field in cls.get_optional_fields():
            if field in msg_data:
                history_dict[field] = msg_data[field]
                
        return history_dict

class MessageBuilder:
    """Builder class responsible for creating and validating message objects.
    Handles the construction of Message instances with proper field validation.
    """
    def __init__(self):
        """Initialize builder with list of optional message fields"""
        self.message_fields = Message.get_optional_fields()

    def build_message(self, query: str, **kwargs) -> Message:
        """Constructs a Message object from provided data.
        
        Args:
            query: Main message content
            **kwargs: Optional fields and their values
            
        Returns:
            Constructed Message object
        """
        message_data = {'query': query}
        for field in self.message_fields:
            if field in kwargs:
                message_data[field] = kwargs[field]
        return Message(**message_data)

class RedisHandler:
    """Redis processing class responsible for all interactions with Redis.
    Handles storage, retrieval, and manipulation of message data.
    
    This class provides a comprehensive interface for:
    - Storing messages in Redis
    - Retrieving individual messages and conversation histories
    - Managing conversation blocks
    - Generating conversation IDs
    """
    def __init__(self):
        """Initialize RedisHandler with Redis client and MessageBuilder.
        
        Establishes connection to Redis server using configuration parameters:
        - REDIS_HOST: Redis server host address
        - REDIS_PORT: Redis server port number
        - db=0: Default Redis database
        - decode_responses=True: Automatically decode Redis responses to strings
        """
        self.client = redis.StrictRedis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=0, 
            decode_responses=True
        )
        self.message_builder = MessageBuilder()
        self.message_fields = Message.get_optional_fields()

    def _build_redis_key(self, conversation_block_id: Union[str, int], conv_id: str) -> str:
        """Constructs a Redis key by combining block ID and conversation ID.
        
        Args:
            conversation_block_id: Identifier for the conversation block
            conv_id: Individual conversation identifier
            
        Returns:
            Formatted Redis key string in format 'block_id:conv_id'
        """
        return f"{str(conversation_block_id)}:{conv_id}"

    def store_query(self, conv_id: str, query: str, conversation_block_id: Union[str, int], 
                   **kwargs) -> Union[str, bool]:
        """Stores a query message in Redis with optional metadata.
        
        Args:
            conv_id: Unique identifier for the conversation
            query: Content of the message to store
            conversation_block_id: Identifier for the conversation block
            **kwargs: Optional parameters including:
                     - expiration: Time in seconds until message expires
                     - pipeline: Redis pipeline for batch operations
                     - Any additional fields defined in Message class
            
        Returns:
            str: Redis key if stored directly
            bool: True if stored using pipeline
            
        Raises:
            Exception: If storage operation fails
        """
        try:
            expiration = kwargs.pop('expiration', None)
            pipeline = kwargs.pop('pipeline', None)

            # Build message object with all provided fields
            message = self.message_builder.build_message(query, **kwargs)
            redis_key = self._build_redis_key(conversation_block_id, conv_id)
            
            # Choose storage method based on pipeline presence
            if pipeline:
                self._store_with_pipeline(pipeline, conversation_block_id, conv_id, 
                                        message, expiration)
                return True
            else:
                return self._store_direct(conversation_block_id, conv_id, message, 
                                        expiration, redis_key)
                
        except Exception as e:
            print(f"Error in store_query: {str(e)}")
            raise

    def _store_with_pipeline(self, pipeline, conversation_block_id: Union[str, int], 
                           conv_id: str, message: Message, expiration: Optional[int]):
        """Stores message using Redis pipeline for batch operations.
        
        Args:
            pipeline: Redis pipeline instance for batch operations
            conversation_block_id: Block identifier
            conv_id: Conversation identifier
            message: Message object to store
            expiration: Optional expiration time in seconds
        """
        pipeline.hset(conversation_block_id, conv_id, json.dumps(message.to_dict()))
        if expiration:
            pipeline.expire(conversation_block_id, time=expiration)

    def _store_direct(self, conversation_block_id: Union[str, int], conv_id: str, 
                     message: Message, expiration: Optional[int], redis_key: str) -> str:
        """Directly stores message in Redis without pipeline.
        
        Args:
            conversation_block_id: Block identifier
            conv_id: Conversation identifier
            message: Message object to store
            expiration: Optional expiration time in seconds
            redis_key: Constructed Redis key
            
        Returns:
            Redis key for the stored message
        """
        self.client.hset(conversation_block_id, conv_id, json.dumps(message.to_dict()))
        if expiration:
            self.client.expire(conversation_block_id, time=expiration)
        return redis_key

    def get_query(self, redis_key: str) -> str:
        """Retrieves a single query message from Redis using its key.
        
        Args:
            redis_key: Combined key in format 'block_id:conv_id'
            
        Returns:
            str: Query content if found
                 Error message if retrieval fails or query not found
                 
        Note:
            Returns formatted error message instead of raising exception
            to maintain backwards compatibility
        """
        try:
            conversation_block_id, conv_id = redis_key.split(':')
            data = self.client.hget(conversation_block_id, conv_id)
            if data:
                message_data = json.loads(data)
                return message_data.get('query', '')
            return f"No query found in Redis for conversation: {conv_id}"
        except Exception as e:
            return f"Error while fetching query from Redis: {str(e)}"

    def get_conversation_history(self, conversation_block_id: str) -> List[Dict[str, Any]]:
        """Retrieves and formats complete conversation history for a block.
        
        Fetches all messages in the conversation block, formats them into
        a consistent structure, and sorts them by conversation ID.
        
        Args:
            conversation_block_id: Identifier for the conversation block
            
        Returns:
            List[Dict]: Sorted list of formatted message dictionaries containing:
                       - id: Conversation identifier
                       - content: Message content
                       - Additional fields from Message class (sender_id, timestamp, etc.)
                       
        Note:
            Returns empty list if no messages found or error occurs
        """
        try:
            messages = self.get_all_messages(conversation_block_id)
            if not messages:
                return []
            
            history = [
                Message.to_history_format(conv_id, msg_data)
                for conv_id, msg_data in messages.items()
            ]
            
            return sorted(history, 
                         key=lambda x: int(x['id']) if x['id'].isdigit() else float('inf'))
        except Exception as e:
            print(f"Error in get_conversation_history: {str(e)}")
            return []

    def get_all_messages(self, conversation_block_id: str) -> Dict[str, Any]:
        """Retrieves all messages from a conversation block in Redis.
        
        Fetches and deserializes all messages stored under the given block ID.
        
        Args:
            conversation_block_id: Identifier for the conversation block
            
        Returns:
            Dict[str, Any]: Dictionary mapping conversation IDs to message data
                           Empty dict if no messages found or error occurs
        """
        try:
            messages = self.client.hgetall(conversation_block_id)
            return {k: json.loads(v) for k, v in messages.items()}
        except Exception as e:
            print(f"Error fetching all messages: {str(e)}")
            return {}

    def delete_conversation_block(self, conversation_block_id: str) -> bool:
        """Deletes an entire conversation block from Redis.
        
        Removes all messages and metadata associated with the given block ID.
        
        Args:
            conversation_block_id: Identifier for the conversation block to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
            
        Note:
            Returns False instead of raising exception to maintain backwards compatibility
        """
        try:
            return bool(self.client.delete(conversation_block_id))
        except Exception as e:
            print(f"Error deleting conversation block: {str(e)}")
            return False

    def conv_id_generator(self, conversation_block_id: str) -> str:
        """Generates the next available conversation ID for a block.
        
        Finds the highest existing conversation ID in the block and increments it.
        If no conversations exist, starts from "0".
        
        Args:
            conversation_block_id: Identifier for the conversation block
            
        Returns:
            str: Next available conversation ID
                 "0" if no existing conversations
                 "-1" if error occurs
                 
        Note:
            - Only considers numeric conversation IDs
            - Returns string to maintain consistency with existing IDs
        """
        try:
            messages = self.get_all_messages(conversation_block_id)
            if not messages:
                return "0"
            existing_ids = [int(msg_id) for msg_id in messages.keys() if msg_id.isdigit()]
            return str(max(existing_ids) + 1) if existing_ids else "0"
        except Exception as e:
            print(f"Error in conv_id_generator: {str(e)}")
            return "-1"
