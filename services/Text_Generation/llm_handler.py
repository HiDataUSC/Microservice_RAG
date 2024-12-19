from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PromptParams:
    """Parameters for prompt template"""
    question: str = ""
    history: List[HumanMessage | AIMessage] = None

    @classmethod
    def from_kwargs(cls, **kwargs) -> 'PromptParams':
        return cls(
            question=kwargs.get('question', ""),
            history=kwargs.get('history', [])
        )

class GPTPromptStrategy:
    def get_template(self) -> str:
        return """Answer the question based on the conversation history and your knowledge."""

class LLMHandler:
    """Handler for Language Model interactions"""

    def __init__(self):
        """Initialize LLM handler for GPT mode"""
        self.strategy = GPTPromptStrategy()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    def generate_answer(self, **kwargs) -> str:
        """
        Generate answer based on input parameters and chat history
        Args:
            **kwargs: Must include 'question', may include 'history'
        Returns:
            str: Generated answer
        """
        params = PromptParams.from_kwargs(**kwargs)
        
        # 构建消息列表
        messages = [
            SystemMessage(content=self.strategy.get_template())
        ]
        
        # 添加历史记录
        if params.history:
            messages.extend(params.history)
        
        # 添加当前问题
        messages.append(HumanMessage(content=params.question))
        
        # 使用消息列表生成回答
        answer = self.llm.invoke(messages)
        return answer.content
