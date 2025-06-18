from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import time
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

players = {}
scores = {}
host_name = None
last_question = None
last_choices = []
last_answer_index = None
# Load questions from JSON file
QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "questions.json")
with open(QUESTIONS_FILE, "r") as f:
    questions = json.load(f)

current_question = None
current_choices = []
current_round = 0
round_active = False
player_answers = {}
player_answer_times = {}
ROUND_TIME = 15  # seconds
MAX_ROUNDS = 5

game_started = False

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "players": players, "game_started": game_started, "round_active": round_active, "current_question": current_question, "current_choices": current_choices, "current_round": current_round, "scores": scores, "last_question": last_question, "last_choices": last_choices, "last_answer_index": last_answer_index})

@app.post("/join", response_class=RedirectResponse)
async def join(name: str = Form(...)):
    global game_started, scores, current_round, current_question, current_choices, round_active
    if name not in players:
        players[name] = {}
        scores[name] = 0
    # Start the game automatically if not already started
    if not game_started:
        game_started = True
        scores = {n: 0 for n in players}
        current_round = 0
        # Start first question immediately
        q = random.choice(questions)
        current_question = q["question"]
        current_choices = q["choices"]
        round_active = True
        player_answers.clear()
        player_answer_times.clear()
    return RedirectResponse(f"/player/{name}", status_code=302)

@app.get("/player/{name}", response_class=HTMLResponse)
async def player_page(request: Request, name: str):
    role = players.get(name, {}).get("role", "Not joined") if isinstance(players.get(name), dict) else players.get(name, "Not joined")
    return templates.TemplateResponse("index.html", {"request": request, "name": name, "role": role, "players": players, "game_started": game_started, "round_active": round_active, "current_question": current_question, "current_choices": current_choices, "current_round": current_round, "scores": scores, "last_question": last_question, "last_choices": last_choices, "last_answer_index": last_answer_index})

@app.post("/answer", response_class=RedirectResponse)
async def answer(name: str = Form(...), choice: int = Form(...)):
    global round_active, current_question, current_choices, current_round, game_started, last_question, last_choices, last_answer_index
    if round_active and name in players:
        if name not in player_answers:
            player_answers[name] = choice
            player_answer_times[name] = time.time()
        # Score answer immediately
        # Find the current question's answer index
        answer_index = None
        for q in questions:
            if q["question"] == current_question and q["choices"] == current_choices:
                answer_index = q["answer"]
                break
        if answer_index is not None:
            # Only score if correct
            if player_answers[name] == answer_index:
                # Give 1 point for correct
                scores[name] = scores.get(name, 0) + 1
            # Store last question and answer for display
            last_question = current_question
            last_choices = current_choices
            last_answer_index = answer_index
        # Move to next question
        current_round += 1
        if current_round < MAX_ROUNDS:
            q = random.choice(questions)
            current_question = q["question"]
            current_choices = q["choices"]
            round_active = True
            player_answers.clear()
            player_answer_times.clear()
        else:
            game_started = False
            current_question = None
            current_choices = []
            round_active = False
    return RedirectResponse(f"/player/{name}", status_code=302)

@app.get("/reset")
async def reset_game():
    global players, game_started, scores, current_question, current_choices, current_round, round_active, player_answers, host_name
    players = {}
    scores = {}
    game_started = False
    current_question = None
    current_choices = []
    current_round = 0
    round_active = False
    player_answers = {}
    host_name = None
    return RedirectResponse("/", status_code=302)
