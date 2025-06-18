import json
from typing import List

class TriviaQuestion:
    def __init__(self, question: str, answers: List[str]):
        self.question = question
        self.answers = answers
        self.correct_answer = answers[0]  # first answer is correct by design

    def __repr__(self):
        return f"<TriviaQuestion: {self.question}>"
