import pygame
import random
from trivia_machine.models import TriviaQuestion
from trivia_machine.utils import load_trivia_questions

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trivia Game")

FONT = pygame.font.SysFont(None, 32)
BIG_FONT = pygame.font.SysFont(None, 48)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)

# Load questions
questions = load_trivia_questions("trivia_machine/assets/qs_and_as.json")
random.shuffle(questions)

current_q_index = 0
score = 0
TOTAL_QUESTIONS = 10

def draw_text(text, x, y, font=FONT, color=BLACK):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_text_wrapped(text, x, y, font=FONT, color=BLACK, max_width=WIDTH - 40, line_height=40):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        surface = font.render(line, True, color)
        screen.blit(surface, (x, y + i * line_height))

def show_question(q: TriviaQuestion, shuffled_answers):
    screen.fill(WHITE)
    draw_text(f"Question {current_q_index + 1} of {TOTAL_QUESTIONS}", 20, 20, BIG_FONT)
    draw_text_wrapped(q.question, 20, 80)

    for i, ans in enumerate(shuffled_answers):
        draw_text(f"{i + 1}. {ans}", 40, 180 + i * 50)

    draw_text("Press 1, 2, 3... to answer", 20, HEIGHT - 60)

def show_result():
    screen.fill(WHITE)
    draw_text("Game Over!", 300, 200, BIG_FONT)
    draw_text(f"Final Score: {score} / {TOTAL_QUESTIONS}", 280, 300, BIG_FONT)
    draw_text("Press ESC to Quit", 300, 400)

running = True
showing_result = False
shuffled_answers = []
correct_answer = ""

# Initialize first question
if questions:
    q = questions[current_q_index]
    shuffled_answers = q.answers.copy()
    random.shuffle(shuffled_answers)
    correct_answer = q.answers[0]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if showing_result:
                if event.key == pygame.K_ESCAPE:
                    running = False
            else:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    answer_index = event.key - pygame.K_1
                    if answer_index < len(shuffled_answers):
                        if shuffled_answers[answer_index] == correct_answer:
                            score += 1
                        current_q_index += 1
                        if current_q_index >= TOTAL_QUESTIONS or current_q_index >= len(questions):
                            showing_result = True
                        else:
                            q = questions[current_q_index]
                            shuffled_answers = q.answers.copy()
                            random.shuffle(shuffled_answers)
                            correct_answer = q.answers[0]

    if showing_result:
        show_result()
    else:
        show_question(questions[current_q_index], shuffled_answers)

    pygame.display.flip()

pygame.quit()
