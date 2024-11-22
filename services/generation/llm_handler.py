from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Protocol, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class PromptParams:
    """Parameters for prompt template"""
    question: str = ""
    context: str = ""
    chat_history: str = ""
    
    @classmethod
    def from_kwargs(cls, **kwargs) -> 'PromptParams':
        return cls(
            question=kwargs.get('question', ""),
            context=kwargs.get('context', ""),
            chat_history=kwargs.get('chat_history', "")
        )

class PromptStrategy(ABC):
    """Abstract base class for prompt strategies"""
    @abstractmethod
    def get_template(self) -> str:
        """Returns the prompt template string"""
        pass

    @abstractmethod
    def format_prompt(self, params: PromptParams) -> Dict[str, Any]:
        """Formats parameters for the prompt"""
        pass

class RAGPromptStrategy(PromptStrategy):
    def get_template(self) -> str:
        return """Previous conversation history:
            {chat_history}
            Context for the current question:
            {context}
            Current question: {question}

            Please provide an answer based on both the context and previous conversation history if relevant."""

    def format_prompt(self, params: PromptParams) -> Dict[str, Any]:
        return {
            'chat_history': params.chat_history,
            'context': params.context,
            'question': params.question
        }

class GPTPromptStrategy(PromptStrategy):
    def get_template(self) -> str:
        return """Previous conversation history:
            {chat_history}
            Current question: {question}
            Please provide an answer based on the conversation history and your knowledge."""

    def format_prompt(self, params: PromptParams) -> Dict[str, Any]:
        return {
            'chat_history': params.chat_history,
            'question': params.question
        }

class LLMHandler:
    """Handler for Language Model interactions"""
    _strategies: Dict[str, PromptStrategy] = {
        'RAG': RAGPromptStrategy(),
        'GPT': GPTPromptStrategy()
    }

    def __init__(self, mode='RAG'):
        """
        Initialize LLM handler
        Args:
            mode: Mode to use ('RAG' or 'GPT')
        """
        if mode not in self._strategies:
            raise ValueError(f"Unsupported mode: {mode}")
            
        self.mode = mode
        self.strategy = self._strategies[mode]
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.prompt = ChatPromptTemplate.from_template(
            self.strategy.get_template()
        )

    def generate_answer(self, **kwargs) -> str:
        """
        Generate answer based on input parameters
        Args:
            **kwargs: May include question, context, chat_history
        Returns:
            str: Generated answer
        """
        params = PromptParams.from_kwargs(**kwargs)
        formatted_params = self.strategy.format_prompt(params)
        filled_prompt = self.prompt.format(**formatted_params)
        answer = self.llm.invoke(filled_prompt)
        return answer.content

    @classmethod
    def register_strategy(cls, mode: str, strategy: PromptStrategy) -> None:
        """
        Register a new prompt strategy
        Args:
            mode: Name of the strategy mode
            strategy: Strategy instance
        """
        cls._strategies[mode] = strategy
