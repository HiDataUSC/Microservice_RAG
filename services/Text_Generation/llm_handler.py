from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class PromptParams:
    """Parameters for prompt template"""
    question: str = ""

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'PromptParams':
        return cls(
            question=kwargs.get('question', "")
        )

class GPTPromptStrategy:
    def get_template(self) -> str:
        return """Current question: {question}
            Please provide an answer based on your knowledge."""

    def format_prompt(self, params: PromptParams) -> Dict[str, Any]:
        return {
            'question': params.question
        }

class LLMHandler:
    """Handler for Language Model interactions"""

    def __init__(self):
        """Initialize LLM handler for GPT mode"""
        self.strategy = GPTPromptStrategy()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.prompt = ChatPromptTemplate.from_template(
            self.strategy.get_template()
        )

    def generate_answer(self, **kwargs) -> str:
        """
        Generate answer based on input parameters
        Args:
            **kwargs: May include question, chat_history
        Returns:
            str: Generated answer
        """
        params = PromptParams.from_kwargs(**kwargs)
        formatted_params = self.strategy.format_prompt(params)
        filled_prompt = self.prompt.format(**formatted_params)
        answer = self.llm.invoke(filled_prompt)
        return answer.content
