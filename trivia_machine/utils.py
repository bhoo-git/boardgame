from trivia_machine.models import TriviaQuestion
from typing import List
import json

def load_trivia_questions(json_path: str) -> List[TriviaQuestion]:
    with open(json_path, 'r') as file:
        data = json.load(file)

    questions = []
    for q in data.get("questions", []):
        question_text = q["question"]
        answers = q["answers"]
        questions.append(TriviaQuestion(question_text, answers))

    return questions
