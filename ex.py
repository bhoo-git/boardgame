from trivia_machine import load_trivia_questions
from trivia_machine import TriviaQuestion

if __name__ == "__main__":
    questions = load_trivia_questions("trivia_machine\\assets\\qs_and_as.json")

    for q in questions:
        print(q.question)
        for idx, answer in enumerate(q.answers, start=1):
            print(f"  {idx}. {answer}")
        print(f"Correct Answer: {q.correct_answer}\n")
