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
        """Format external conversation history for context"""
        formatted_history = []
        for msg in history:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content.strip()
            if content:
                # 添加更明确的标记来突出重要信息
                if any(keyword in content.lower() for keyword in ['deadline', 'ddl', 'due date']):
                    formatted_history.append(f"[IMPORTANT] {role}: {content}")
                else:
                    formatted_history.append(f"{role}: {content}")
        
        return "\n".join([
            f"\nRelevant conversation from block {source_id}:",
            *formatted_history,
            "\n"
        ])

    def generate_answer(self, **kwargs) -> str:
        params = PromptParams.from_kwargs(**kwargs)
        
        messages = [
            SystemMessage(content="""You are a helpful AI assistant engaged in a conversation. 
            When answering questions:
            1. Always check the provided context for relevant information
            2. If a question refers to information in previous conversations, use that information directly
            3. For questions about dates, deadlines, or events, refer to the specific dates mentioned in the context
            4. Be direct and specific when the information is available in the context
            5. Only ask for clarification if the information is not available in any context""")
        ]
        
        # Add current conversation history
        if params.current_history:
            messages.extend(params.current_history)
        
        # Add external sources with clear separation
        if params.external_sources:
            context_messages = []
            for source in params.external_sources:
                if source['type'] == 'conversation_history':
                    formatted_context = self._format_external_history(source['content'], source['source_id'])
                    context_messages.append(SystemMessage(content=formatted_context))
            
            if context_messages:
                messages.append(SystemMessage(content="=== Relevant Context ==="))
                messages.extend(context_messages)
                messages.append(SystemMessage(content="=== End Context ==="))
        
        # Add focusing prompt
        messages.append(SystemMessage(content="""Now, answer the user's question:
        - If the question refers to information in the context, use that information directly
        - Be specific and reference the exact information from the context
        - Only ask for clarification if the information is truly missing"""))
        
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
