
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

players = {}
locations = ["Beach", "Casino", "Submarine", "Theater", "Restaurant"]
game_started = False
selected_location = ""
spy_name = ""

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "players": players, "game_started": game_started})

@app.post("/join", response_class=RedirectResponse)
async def join(name: str = Form(...)):
    if name not in players:
        players[name] = ""
    return RedirectResponse(f"/player/{name}", status_code=302)

@app.get("/player/{name}", response_class=HTMLResponse)
async def player_page(request: Request, name: str):
    role = players.get(name, "Not joined")
    return templates.TemplateResponse("index.html", {"request": request, "name": name, "role": role, "players": players, "game_started": game_started})

@app.get("/start")
async def start_game():
    global game_started, selected_location, spy_name
    game_started = True
    selected_location = random.choice(locations)
    spy_name = random.choice(list(players.keys()))
    for name in players:
        players[name] = "Spy" if name == spy_name else selected_location
    return RedirectResponse("/", status_code=302)

@app.get("/reset")
async def reset_game():
    global players, game_started, selected_location, spy_name
    players = {}
    game_started = False
    selected_location = ""
    spy_name = ""
    return RedirectResponse("/", status_code=302)
