from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
import asyncio
import time
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

players = {}
scores = {}
# Removed: locations = [ ... ]
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

async def round_timer():
    global round_active, current_question, current_choices, player_answers, current_round, game_started
    while game_started and current_round < MAX_ROUNDS:
        round_active = True
        player_answers = {}
        player_answer_times = {}
        q = random.choice(questions)
        current_question = q["question"]
        current_choices = q["choices"]
        answer_index = q["answer"]
        start_time = time.time()
        await asyncio.sleep(ROUND_TIME)
        # Score answers
        correct_players = []
        for name in players:
            if name in player_answers and player_answers[name] == answer_index:
                correct_players.append((name, player_answer_times.get(name, float('inf'))))
        # Sort by answer time (fastest first)
        correct_players.sort(key=lambda x: x[1])
        for idx, (name, _) in enumerate(correct_players):
            # 1 point for correct, +1 for first, +0.5 for second
            bonus = 0
            if idx == 0:
                bonus = 1
            elif idx == 1:
                bonus = 0.5
            scores[name] = scores.get(name, 0) + 1 + bonus
        round_active = False
        current_round += 1
        await asyncio.sleep(3)  # Short pause between rounds
    game_started = False
    current_question = None
    current_choices = []
    current_round = 0

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "players": players, "game_started": game_started, "round_active": round_active, "current_question": current_question, "current_choices": current_choices, "current_round": current_round, "scores": scores})

@app.post("/join", response_class=RedirectResponse)
async def join(name: str = Form(...)):
    global host_name
    if name not in players:
        players[name] = ""
        scores[name] = 0
        if host_name is None:
            host_name = name  # First player is host
    return RedirectResponse(f"/player/{name}", status_code=302)

@app.get("/player/{name}", response_class=HTMLResponse)
async def player_page(request: Request, name: str):
    role = players.get(name, "Not joined")
    is_host = (name == host_name)
    return templates.TemplateResponse("index.html", {"request": request, "name": name, "role": role, "players": players, "game_started": game_started, "round_active": round_active, "current_question": current_question, "current_choices": current_choices, "current_round": current_round, "scores": scores, "is_host": is_host, "host_name": host_name})

@app.post("/answer", response_class=RedirectResponse)
async def answer(name: str = Form(...), choice: int = Form(...)):
    if round_active and name in players:
        if name not in player_answers:
            player_answers[name] = choice
            player_answer_times[name] = time.time()
    return RedirectResponse(f"/player/{name}", status_code=302)

@app.get("/start")
async def start_game(request: Request, background_tasks: BackgroundTasks, name: str = None):
    global game_started, scores, current_round
    # Only host can start
    if name != host_name:
        return RedirectResponse("/", status_code=302)
    if len(players) < 1:
        return RedirectResponse("/", status_code=302)
    game_started = True
    scores = {name: 0 for name in players}
    current_round = 0
    background_tasks.add_task(round_timer)
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
