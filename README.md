# 🎲 RAS Trivia Game

A lightweight FastAPI web app to host a local boardgame implementation and serve over the Wi-Fi network. 4 FUN lol.
---

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
pip install fastapi uvicorn jinja2
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