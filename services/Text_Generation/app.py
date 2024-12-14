from llm_handler import LLMHandler

class Generation:
    def __init__(self):
        self.llm_handler = LLMHandler()

    def generate_answer(self, query: str) -> str:
        """
        Generate an answer based on the query.
        :param query: User's query
        :return: Generated answer as a string
        """

        answer = self.llm_handler.generate_answer(
            question=query
        )

        return answer
