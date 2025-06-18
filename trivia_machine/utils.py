from trivia_machine.models import TriviaQuestion
from typing import List
import json

def load_trivia_questions(json_path: str) -> List[TriviaQuestion]:
    with open(json_path, 'r') as file:
        data = json.load(file)

    questions = []
    # Iterate over each topic, then each question within that topic
    for topic in data.get("topics", []):
        for q in topic.get("questions", []):
            question_text = q["question"]
            answers = q["answers"]
            # Optionally, you could also store topic if TriviaQuestion supports it
            questions.append(TriviaQuestion(question_text, answers))

    return questions
