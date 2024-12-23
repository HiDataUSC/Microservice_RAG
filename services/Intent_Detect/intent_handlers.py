from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import boto3
import json
import os

class BaseIntentHandler(ABC):
    """Base class for all intent handlers"""
    
    def __init__(self):
        self.chain = (
            PromptTemplate.from_template(self.get_prompt_template())
            | ChatOpenAI(
                model_name="gpt-3.5-turbo", 
                temperature=0.7
            )
            | StrOutputParser()
        )
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Return the prompt template for this handler"""
        pass
    
    @abstractmethod
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the intent with given data"""
        pass

class ConversationHandler(BaseIntentHandler):
    """Handler for conversation intent (ID: 2)"""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.text_generation_function = os.environ.get('TEXT_GENERATION_FUNCTION', 'Text_Generation')
    
    def get_prompt_template(self) -> str:
        pass
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print(f"Invoking Text Generation with data: {data}")
            print(f"Using function name: {self.text_generation_function}")
            
            response = self.lambda_client.invoke(
                FunctionName=self.text_generation_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(data)
            )
            
            result = json.loads(response['Payload'].read().decode())
            print(f"Text Generation response: {result}")
            return result
            
        except Exception as e:
            print(f"Error in ConversationHandler: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': str(e)
                })
            }

class ProjectPlanningHandler(BaseIntentHandler):
    """Handler for project planning intent (ID: 1)"""
    
    def get_prompt_template(self) -> str:
        return """As a project planning assistant, help create a plan based on the user's input.
                Consider the following aspects:
                - Project scope and objectives
                - Key milestones and timeline
                - Required resources
                
                User Input: {query}
                
                Response:"""
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.chain.invoke({
                "query": data.get("query", "")
            })
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'action': 'project_planning',
                    'response': response,
                    'workspace_id': data.get('workspace_id'),
                    'block_id': data.get('block_id')
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'status': 'error',
                    'error': str(e)
                })
            }

class DefaultHandler(BaseIntentHandler):
    """Handler for other/unknown intents (ID: 3, -1)"""
    
    def get_prompt_template(self) -> str:
        return """Provide a helpful response to the user's query.
                
                User Query: {query}
                Response:"""
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.chain.invoke({
                "query": data.get("query", "")
            })
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'action': 'default',
                    'response': response,
                    'workspace_id': data.get('workspace_id'),
                    'block_id': data.get('block_id')
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'status': 'error',
                    'error': str(e)
                })
            }

class IntentHandlerFactory:
    """Factory class to create appropriate intent handlers"""
    
    _handlers = {
        1: ProjectPlanningHandler(),
        2: ConversationHandler(),
        3: DefaultHandler(),
        -1: DefaultHandler()
    }
    
    @classmethod
    def get_handler(cls, intent_id: int) -> BaseIntentHandler:
        """Get appropriate handler for given intent ID"""
        return cls._handlers.get(intent_id, cls._handlers[3])