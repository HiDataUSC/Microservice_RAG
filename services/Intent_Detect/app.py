from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List, Tuple
from enum import Enum
import boto3
import json
import os

class IntentCategory(Enum):
    PROJECT_PLANNING = ("project_planning", 1)  # For project drafting/planning requests
    CONVERSATION = ("conversation", 2)          # For general conversation
    OTHER = ("other", 3)                       # For any other types of requests
    UNKNOWN = ("unknown", -1)                  # For unknown or error cases
    
    def __init__(self, value, id):
        self._value_ = value
        self.id = id
    
    @classmethod
    def get_prompt_categories(cls) -> str:
        """Get formatted categories for prompt template, excluding UNKNOWN"""
        return "\n".join([f"- {intent.value}" for intent in cls 
                         if intent != cls.UNKNOWN])

    @classmethod
    def is_valid(cls, intent: str) -> bool:
        """Check if the given intent is a valid category"""
        return intent in [e.value for e in cls]
    
    @classmethod
    def get_id_by_value(cls, value: str) -> int:
        """Get intent ID by its value"""
        for intent in cls:
            if intent.value == value:
                return intent.id
        return cls.UNKNOWN.id

class ConversationHistory:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(os.environ['DB_TABLE_NAME'])
    
    def get_history(self, workspace_id: str, block_id: str) -> List[Dict[str, str]]:
        """获取指定区块的对话历史"""
        try:
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('workspace_id').eq(workspace_id) & 
                                     boto3.dynamodb.conditions.Key('sort_key').begins_with(f"{workspace_id}#{block_id}#")
            )
            
            history = []
            for item in response.get('Items', []):
                if 'messages' not in item:
                    continue
                    
                messages = item.get('messages', [])
                if not isinstance(messages, list):
                    continue
                    
                for message in messages:
                    content = message.get('content', '')
                    if content:
                        history.append(content)
            
            return history
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return []

class IntentDetector:
    def __init__(self):
        self.conversation_history = ConversationHistory()
        self.prompt_template = """Analyze the user input and classify it into one of the following categories:
                {categories}

                Consider the following context when classifying:
                - If the input is asking about information mentioned in previous conversations
                - If the input is a follow-up question
                - If the input is requesting information from chat history
                - If the input is referring to any previously mentioned dates, deadlines, or events

                Previous conversations from connected blocks:
                {context}

                Current conversation:
                {current_chat}

                Input to classify:
                {text}

                Important classification rules:
                1. If the input is asking about any information from previous conversations, classify as 'conversation'
                2. If the input refers to previously mentioned dates or deadlines, classify as 'conversation'
                3. If the input is a follow-up question to any previous topic, classify as 'conversation'
                4. Only classify as 'project_planning' for new project requests, not for questions about existing ones

                Return only one classification word from the categories, without any additional content.

                Classification:"""
        
        self.chain = (
            PromptTemplate.from_template(self.prompt_template)
            | ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.3,
                max_tokens=10,
                request_timeout=3
            )
            | StrOutputParser()
        )

    def _get_connected_history(self, connections: list) -> str:
        """获取连接的区块的聊天历史"""
        print(f"Processing connections: {json.dumps(connections, indent=2)}")  # 打印连接信息
        
        if not connections:
            print("No connections found")
            return ""
        
        all_history = []
        for conn in connections:
            block_id = conn.get('id')
            if not block_id:
                print(f"Skipping connection without block_id: {conn}")
                continue
                
            print(f"Getting history for block_id: {block_id}")  # 打印正在处理的 block_id
            
            # 从 DynamoDB 获取历史记录
            history = self.conversation_history.get_history(
                workspace_id=os.environ.get('WORKSPACE_ID', '1'),
                block_id=block_id
            )
            
            print(f"Retrieved history for block {block_id}: {json.dumps(history, indent=2)}")  # 打印获取到的历史记录
            
            if history:
                all_history.extend(history)
        
        final_history = "\n".join(all_history) if all_history else ""
        print(f"Final combined history: {final_history}")  # 打印最终组合的历史记录
        return final_history

    def _get_current_history(self, workspace_id: str, block_id: str) -> str:
        """获取当前区块的聊天历史"""
        if not block_id:
            return ""
            
        history = self.conversation_history.get_history(
            workspace_id=workspace_id,
            block_id=block_id
        )
        return "\n".join(history) if history else ""

    def _get_prediction(self, text: str, categories: str, context: str = "", current_chat: str = "") -> str:
        try:
            intent = self.chain.invoke({
                "text": text,
                "categories": categories,
                "context": context,
                "current_chat": current_chat
            })
            return intent.lower()
        except Exception:
            return None

    def _check_context_relevance(self, text: str, context: str) -> bool:
        """检查输入是否与历史上下文相关"""
        # 转换为小写进行比较
        text_lower = text.lower()
        context_lower = context.lower()
        
        # 定义关键词和其变体
        keywords = {
            'ddl': ['ddl', 'deadline', 'due date'],
            'time': ['when', 'time', 'date'],
            'reference': ['mentioned', 'said', 'told', 'previous'],
            'question_words': ['what', 'when', 'where', 'who', 'why', 'how']
        }
        
        # 检查输入中的关键词是否在上下文中有相关信息
        for category, words in keywords.items():
            for word in words:
                if word in text_lower and word in context_lower:
                    print(f"Found contextual relevance: '{word}' in both input and context")
                    return True
        
        return False

    def detect(self, text: str, workspace_id: str = None, block_id: str = None, connections: list = None) -> Dict[str, Any]:
        try:
            print(f"\n=== Starting Intent Detection ===")
            print(f"Input text: {text}")
            print(f"Workspace ID: {workspace_id}")
            print(f"Block ID: {block_id}")
            print(f"Connections: {json.dumps(connections, indent=2)}")
            
            # 获取连接的区块的历史记录
            context = self._get_connected_history(connections)
            print(f"Connected blocks context: {context}")
            
            # 获取当前对话的历史记录
            current_chat = self._get_current_history(workspace_id, block_id)
            print(f"Current chat history: {current_chat}")
            
            # 首先检查是否与历史上下文相关
            if context and self._check_context_relevance(text, context):
                print("Detected context relevance, classifying as conversation")
                return {
                    'intent_id': IntentCategory.CONVERSATION.id,
                    'workspace_id': workspace_id,
                    'block_id': block_id,
                    'connections': connections
                }
            
            # 如果没有直接的上下文关联，再进行 GPT 分类
            intent = self._get_prediction(
                text=text,
                categories=IntentCategory.get_prompt_categories(),
                context=context,
                current_chat=current_chat
            )
            print(f"Predicted intent: {intent}")
            
            intent_id = IntentCategory.get_id_by_value(intent) if intent and IntentCategory.is_valid(intent) else IntentCategory.OTHER.id
            print(f"Final intent_id: {intent_id}")
            
            result = {
                'intent_id': intent_id,
                'workspace_id': workspace_id,
                'block_id': block_id,
                'connections': connections
            }
            print(f"Returning result: {json.dumps(result, indent=2)}")
            print("=== Intent Detection Complete ===\n")
            return result
            
        except Exception as e:
            print(f"Error in detect: {str(e)}")
            return {
                'intent_id': IntentCategory.OTHER.id,
                'error': str(e),
                'workspace_id': workspace_id,
                'block_id': block_id,
                'connections': connections
            } 