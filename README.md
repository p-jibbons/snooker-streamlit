# Snooker Scoreboard

Rule-aware Streamlit app for tracking a two-player snooker frame, with lightweight running match score.

## What it does

- Tracks two-player frame scores
- Tracks match score across frames with configurable best-of length
- Keeps a lightweight completed-frame history with winner and final score
- Supports simple player registration backed by SQLite
- Enforces red/colour turn order
- Allows multiple reds in a single legal shot
- Handles the final-red transition correctly
- Enforces ordered colour clearance: yellow to black
- Supports a re-spotted black decider when the frame is level after all colours
- Tracks current break
- Awards foul points to the opponent
- Shows points remaining and whether snookers are required
- Supports undo and frame reset
- Auto-saves frame and match state locally during runtime
- Includes unit tests for core game rules and persistence
- Supports continuous test watching

## Project structure

- `app.py` — Streamlit UI
- `snooker/game.py` — game rules and scoring model
- `snooker/storage.py` — JSON + SQLite persistence/bootstrap helpers
- `tests/test_game.py` — unit tests
- `tests/test_storage.py` — persistence tests
- `docs/rules-summary.md` — plain-English rules captured by the app
- `docs/sql-persistence-plan.md` — staged SQL persistence plan

## Repository guardrails (for humans and agents)

- Do not commit personal runtime match data or local SQLite state.
- Keep saved player examples generic (for example, Player1 and Player2) in tracked files.
- Never commit secrets or tokens; keep local secrets in `.env` or `.streamlit/secrets.toml`.
- Prefer small, focused commits that keep tests passing.
- Preserve game rules behavior unless a task explicitly asks for a rules change.

## Run the app

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```powershell
.\.venv\Scripts\python -m pytest
```

## Continuous unit testing

```powershell
.\.venv\Scripts\ptw
```

If `ptw` is not on PATH, use:

```powershell
.\.venv\Scripts\python -m pytest_watch
```
