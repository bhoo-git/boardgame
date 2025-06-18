from fastapi import (
    FastAPI,
    Request,
    Form,
    BackgroundTasks,
    Cookie
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from trivia_machine import load_trivia_questions
from trivia_machine import TriviaQuestion

import random
import asyncio
import time
import json
import os

# ──────────────────────────────────────────────────────────
#  Basic setup
# ──────────────────────────────────────────────────────────
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ――― Game state ―――
players: dict[str, str] = {}
scores:  dict[str, float] = {}

questions = load_trivia_questions("trivia_machine\\assets\\qs_and_as.json")

current_question: str | None = None
current_choices:  list[str] = []
current_round:    int       = 0
round_active:     bool      = False
player_answers:   dict[str, int] = {}
player_answer_times: dict[str, float] = {}

ROUND_TIME = 15           # sec
MAX_ROUNDS = 5
game_started = False

# ――― Admin ―――
ADMIN_PASSWORD = "1234"
ADMIN_COOKIE   = "trivia_admin"    # simple cookie flag

# ──────────────────────────────────────────────────────────
#  Helper: admin panel HTML
# ──────────────────────────────────────────────────────────
def make_admin_panel_html() -> str:
    player_list = "<br>".join(players) or "No players yet."
    return f"""
    <h2>Admin Panel</h2>
    <p><strong>Players joined:</strong><br>{player_list}</p>

    <form method="post" action="/start">
        <button type="submit">Start Game</button>
    </form>

    <br>
    <a href="/reset"><button>Reset Game</button></a>
    """

# ──────────────────────────────────────────────────────────
#  Timer coroutine
# ──────────────────────────────────────────────────────────
async def round_timer():
    global round_active, current_question, current_choices
    global player_answers, player_answer_times, current_round
    global game_started

    while game_started and current_round < MAX_ROUNDS:
        # pick question
        q = random.choice(questions)
        current_question = q["question"]
        current_choices  = q["choices"]
        answer_index     = q["answer"]

        round_active = True
        player_answers.clear()
        player_answer_times.clear()
        start_time = time.time()

        await asyncio.sleep(ROUND_TIME)

        # score
        correct = [
            (name, player_answer_times.get(name, float("inf")))
            for name, ans in player_answers.items()
            if ans == answer_index
        ]
        correct.sort(key=lambda x: x[1])      # fastest first

        for idx, (name, _) in enumerate(correct):
            bonus = 1 if idx == 0 else 0.5 if idx == 1 else 0
            scores[name] = scores.get(name, 0) + 1 + bonus

        round_active   = False
        current_round += 1
        await asyncio.sleep(3)                # short pause

    # game over
    game_started      = False
    current_question  = None
    current_choices   = []
    current_round     = 0

# ──────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "players": players,
            "game_started": game_started,
            "round_active": round_active,
            "current_question": current_question,
            "current_choices": current_choices,
            "current_round": current_round,
            "scores": scores,
        },
    )

# ── Player joins ──────────────────────────────────────────
@app.post("/join", response_class=RedirectResponse)
async def join(name: str = Form(...)):
    if name not in players:
        players[name] = ""
        scores[name]  = 0
    return RedirectResponse(f"/player/{name}", status_code=302)

@app.get("/player/{name}", response_class=HTMLResponse)
async def player_page(request: Request, name: str):
    if name not in players:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "name": name,
            "players": players,
            "game_started": game_started,
            "round_active": round_active,
            "current_question": current_question,
            "current_choices": current_choices,
            "current_round": current_round,
            "scores": scores,
        },
    )

# ── Player submits answer ─────────────────────────────────
@app.post("/answer", response_class=RedirectResponse)
async def answer(name: str = Form(...), choice: int = Form(...)):
    if round_active and name in players and name not in player_answers:
        player_answers[name] = choice
        player_answer_times[name] = time.time()
    return RedirectResponse(f"/player/{name}", status_code=302)

# ── Admin: login page ─────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request, auth: str | None = Cookie(None)):
    if auth == ADMIN_PASSWORD:          # already authenticated
        return HTMLResponse(make_admin_panel_html())

    # show login form
    return HTMLResponse("""
        <h2>Admin Login</h2>
        <form method="post" action="/admin">
            <input type="password" name="password" placeholder="Enter admin password" required>
            <button type="submit">Login</button>
        </form>
    """)

# ── Admin: handle login form ───────────────────────────────
@app.post("/admin", response_class=HTMLResponse)
async def admin_login(password: str = Form(...)):
    if password != ADMIN_PASSWORD:
        return HTMLResponse("<h3>Incorrect password.</h3><a href='/admin'>Try again</a>", status_code=401)
    resp = HTMLResponse(make_admin_panel_html())
    resp.set_cookie(ADMIN_COOKIE, ADMIN_PASSWORD, httponly=True)
    return resp

# ── Admin: start game ─────────────────────────────────────
@app.post("/start", response_class=RedirectResponse)
async def start_game(background_tasks: BackgroundTasks, auth: str | None = Cookie(None)):
    global game_started, current_round, scores

    if auth != ADMIN_PASSWORD:
        return RedirectResponse("/admin", status_code=302)

    if game_started or len(players) == 0:
        return RedirectResponse("/admin", status_code=302)

    game_started  = True
    current_round = 0
    scores        = {n: 0 for n in players}
    background_tasks.add_task(round_timer)
    return RedirectResponse("/admin", status_code=302)

# ── Reset everything ──────────────────────────────────────
@app.get("/reset", response_class=RedirectResponse)
async def reset_game():
    global players, scores, game_started, current_question, current_choices
    global current_round, round_active, player_answers

    players.clear()
    scores.clear()
    game_started      = False
    current_question  = None
    current_choices   = []
    current_round     = 0
    round_active      = False
    player_answers.clear()
    return RedirectResponse("/", status_code=302)
