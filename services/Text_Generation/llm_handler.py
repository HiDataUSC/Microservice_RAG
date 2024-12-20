from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PromptParams:
    """
    Parameters container for LLM prompts.
    
    Attributes:
        question: User's input query
        current_history: Current conversation messages
        external_sources: Additional knowledge sources
    """
    question: str = ""
    current_history: List[HumanMessage | AIMessage] = None
    external_sources: List[Dict] = None

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'PromptParams':
        """Create PromptParams instance from keyword arguments"""
        return cls(
            question=kwargs.get('question', ""),
            current_history=kwargs.get('current_history', []),
            external_sources=kwargs.get('external_sources', [])
        )

class GPTPromptStrategy:
    """Handles the creation of system prompts for the LLM"""
    
    def get_template(self, external_types: List[str]) -> str:
        """
        Generate appropriate system prompt based on available external sources.
        
        Args:
            external_types: List of external source types available
            
        Returns:
            str: Formatted system prompt
        """
        base_prompt = """You are a helpful AI assistant engaged in a conversation. 
        Your primary focus is to provide clear, relevant, and contextual responses to the current conversation."""
        
        if 'conversation_history' in external_types:
            return base_prompt + """
            
            You have access to related conversations from other discussion threads. When relevant:
            1. Draw insights from these related conversations to provide more informed answers
            2. Make connections between current topics and related discussions
            3. Use this additional context to provide more comprehensive responses
            
            However, remember to:
            - Stay focused on the current user's question
            - Only reference related information when it directly adds value
            - Maintain a natural conversation flow
            - Be concise and clear in your responses"""
        
        return base_prompt

class LLMHandler:
    """Handles interactions with the Language Model"""

    def __init__(self):
        """Initialize LLM handler with GPT model and prompt strategy"""
        self.strategy = GPTPromptStrategy()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    def _format_external_history(self, history: List[HumanMessage | AIMessage], source_id: str) -> str:
        """
        Format external conversation history for context.
        
        Args:
            history: List of conversation messages
            source_id: ID of the source block
            
        Returns:
            str: Formatted context information
        """
        # Sort history by timestamp
        sorted_history = sorted(history, 
                              key=lambda x: x.additional_kwargs.get('timestamp', '') 
                              if hasattr(x, 'additional_kwargs') else '')
        
        # Create a more structured summary
        summary_parts = []
        summary_parts.append(f"Related discussion from conversation {source_id}:")
        
        for msg in sorted_history:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content.strip()
            # Only include substantive messages
            if content and len(content) > 5:
                summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)

    def generate_answer(self, **kwargs) -> str:
        """
        Generate answer using LLM based on input parameters.
        
        Args:
            **kwargs: Must include 'question', may include 'current_history' and 'external_sources'
            
        Returns:
            str: Generated answer from LLM
        """
        params = PromptParams.from_kwargs(**kwargs)
        
        # Get all external source types
        external_types = list(set(source['type'] for source in params.external_sources))
        
        # Build message list starting with system prompt
        messages = [
            SystemMessage(content=self.strategy.get_template(external_types))
        ]
        
        # Add current conversation history first
        if params.current_history:
            messages.extend(params.current_history)
        
        # Add external sources as reference information
        if params.external_sources:
            messages.append(SystemMessage(content="""Reference information from related discussions:
            The following are relevant conversations that may provide additional context for your response."""))
            
            for source in params.external_sources:
                source_type = source['type']
                content = source['content']
                source_id = source['source_id']
                
                if source_type == 'conversation_history':
                    formatted_context = self._format_external_history(content, source_id)
                    messages.append(SystemMessage(content=formatted_context))

        # Add a focusing prompt before the user's question
        messages.append(SystemMessage(content="""Now, focus on answering the user's current question. 
        Use the above context only if it helps provide a better response."""))
        
        messages.append(HumanMessage(content=params.question))
        
        answer = self.llm.invoke(messages)
        return answer.content

    def _summarize_conversation(self, history: List[HumanMessage | AIMessage]) -> str:
        """
        Convert conversation history to a readable summary format.
        
        Args:
            history: List of conversation messages
            
        Returns:
            str: Formatted conversation summary
        """
        summary = []
        for msg in history:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content
            summary.append(f"{role}: {content}")
        return "\n".join(summary)
