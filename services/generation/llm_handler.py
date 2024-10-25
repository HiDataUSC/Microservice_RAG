from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class LLMHandler:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.prompt_template = (
            "Answer the question based only on the following context:\n"
            "{context}\n\n"
            "Question: {question}\n"
        )
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)

    def generate_answer(self, context: str, question: str) -> str:
        filled_prompt = self.prompt.format(context=context, question=question)
        answer = self.llm.invoke(filled_prompt)
        return answer.content
