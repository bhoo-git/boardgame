# 🎲 RAS Trivia Game

A lightweight FastAPI web app to host a local boardgame implementation and serve over the Wi-Fi network. 4 FUN lol.
---
# TODOs:

Access to webpage

Get a prompt to enter your username and join the game.

You're in the game.

While you are in the game, every N number of seconds a new round starts.

When a new round starts, a question pops up with 4 multiple choice answers.

You submit your answer, and you get a scoreboard.


[] 

## 🚀 Quick Start

### 1. Clone or Download
Unzip or clone this project:
```bash
unzip boardgame_fastapi.zip
cd boardgame
```

### 2. Install Dependencies
Make sure Python 3.9+ is installed.

Then install required packages:

```bash
python3 -m venv .venv
source bin/.venv/activate
pip install -r requirements.txt
```

### 3. Run the Server
Start the app on your local network:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Get your local IP address (e.g. 192.168.1.42) using:

```bash
ipconfig (Windows)
ifconfig (Linux/macOS)
```
### 4. Share the Link
Tell other players to join via their browser:

```bash
http://<your-local-IP>:8000
```