from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class LLMHandler:
    def __init__(self,mode='RAG'):
        self.mode = mode
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.prompt_template = {
            'RAG': "Answer the question based only on the following context:\n"
            "{context}\n\n"
            "Question: {question}\n",
            'GPT': "Please generate an answer based on your knowledge.\n\n"
            "Question: {question}\n"
        }
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template[self.mode])

    def generate_answer(self, *args, **kwargs) -> str:
        question = kwargs.get('question', "")
        context = kwargs.get('context', "")
        if self.mode == 'RAG':
            filled_prompt = self.prompt.format(context=context, question=question)
        elif self.mode == 'GPT':
            filled_prompt = self.prompt.format(question=question)
        answer = self.llm.invoke(filled_prompt)
        return answer.content
