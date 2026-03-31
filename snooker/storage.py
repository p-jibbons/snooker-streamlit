from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from .game import Ball, SnookerGame


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SAVE_FILE = DATA_DIR / "current_frame.json"
MATCH_FILE = DATA_DIR / "match_state.json"
DB_FILE = DATA_DIR / "snooker.db"


APP_STATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS app_state (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

MATCHES_SCHEMA = """
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    player1_id INTEGER NULL,
    player2_id INTEGER NULL,
    player1_name_snapshot TEXT NOT NULL,
    player2_name_snapshot TEXT NOT NULL,
    best_of INTEGER NOT NULL,
    frames_won_p1 INTEGER NOT NULL DEFAULT 0,
    frames_won_p2 INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'in_progress',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT NULL
)
"""

FRAMES_SCHEMA = """
CREATE TABLE IF NOT EXISTS frames (
    id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    frame_number INTEGER NOT NULL,
    winner_player_slot INTEGER NULL,
    winner_player_id INTEGER NULL,
    winner_name_snapshot TEXT NULL,
    player1_score INTEGER NOT NULL,
    player2_score INTEGER NOT NULL,
    ended_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

PLAYERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    display_name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER NOT NULL DEFAULT 1
)
"""


def _serialize_game(game: SnookerGame) -> Dict[str, Any]:
    payload = asdict(game)
    payload["colours_cleared"] = [ball.value for ball in game.colours_cleared]
    return payload


def _deserialize_game(payload: Dict[str, Any]) -> SnookerGame:
    payload = dict(payload)
    payload["colours_cleared"] = [Ball(value) for value in payload.get("colours_cleared", [])]
    return SnookerGame(**payload)


def get_connection(path: Path = DB_FILE) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def bootstrap_db(path: Path = DB_FILE) -> Path:
    with get_connection(path) as conn:
        conn.execute(APP_STATE_SCHEMA)
        conn.execute(MATCHES_SCHEMA)
        conn.execute(FRAMES_SCHEMA)
        conn.execute(PLAYERS_SCHEMA)
        conn.commit()
    return path


def _save_app_state(key: str, value: Dict[str, Any], path: Path = DB_FILE) -> None:
    bootstrap_db(path)
    payload = json.dumps(value, indent=2)
    with get_connection(path) as conn:
        conn.execute(
            """
            INSERT INTO app_state(key, value_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value_json=excluded.value_json,
                updated_at=CURRENT_TIMESTAMP
            """,
            (key, payload),
        )
        conn.commit()


def _load_app_state(key: str, path: Path = DB_FILE) -> Dict[str, Any] | None:
    bootstrap_db(path)
    with get_connection(path) as conn:
        row = conn.execute("SELECT value_json FROM app_state WHERE key = ?", (key,)).fetchone()
    if row is None:
        return None
    return json.loads(row[0])


def save_game(game: SnookerGame, path: Path = SAVE_FILE, db_path: Path = DB_FILE) -> Path:
    payload = _serialize_game(game)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _save_app_state("current_frame", payload, db_path)
    return path


def load_game(path: Path = SAVE_FILE, db_path: Path = DB_FILE) -> SnookerGame | None:
    payload = _load_app_state("current_frame", db_path)
    if payload is not None:
        return _deserialize_game(payload)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _deserialize_game(payload)


def _default_match_state() -> Dict[str, Any]:
    return {
        "player_names": ["Player 1", "Player 2"],
        "frames_won": [0, 0],
        "best_of": 1,
        "frame_history": [],
    }


def save_match_state(match_state: Dict[str, Any], path: Path = MATCH_FILE, db_path: Path = DB_FILE) -> Path:
    payload = _default_match_state()
    payload.update(match_state)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _save_app_state("current_match", payload, db_path)
    return path


def load_match_state(path: Path = MATCH_FILE, db_path: Path = DB_FILE) -> Dict[str, Any]:
    payload = _load_app_state("current_match", db_path)
    if payload is not None:
        default = _default_match_state()
        default.update(payload)
        return default
    if not path.exists():
        return _default_match_state()
    payload = json.loads(path.read_text(encoding="utf-8"))
    default = _default_match_state()
    default.update(payload)
    return default


def record_completed_frame(
    match_id: int,
    frame_number: int,
    winner_player_slot: int | None,
    winner_name_snapshot: str | None,
    player1_score: int,
    player2_score: int,
    ended_by: str,
    db_path: Path = DB_FILE,
) -> int:
    bootstrap_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO frames(
                match_id,
                frame_number,
                winner_player_slot,
                winner_player_id,
                winner_name_snapshot,
                player1_score,
                player2_score,
                ended_by
            )
            VALUES (?, ?, ?, NULL, ?, ?, ?, ?)
            """,
            (
                match_id,
                frame_number,
                winner_player_slot,
                winner_name_snapshot,
                player1_score,
                player2_score,
                ended_by,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_players(db_path: Path = DB_FILE) -> list[dict[str, Any]]:
    bootstrap_db(db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, display_name, created_at, is_active
            FROM players
            ORDER BY LOWER(display_name), id
            """
        ).fetchall()
    return [
        {
            "id": row[0],
            "display_name": row[1],
            "created_at": row[2],
            "is_active": bool(row[3]),
        }
        for row in rows
    ]


def register_player(display_name: str, db_path: Path = DB_FILE) -> int:
    name = display_name.strip()
    if not name:
        raise ValueError("Player name cannot be empty.")
    bootstrap_db(db_path)
    with get_connection(db_path) as conn:
        existing = conn.execute(
            "SELECT id FROM players WHERE LOWER(display_name) = LOWER(?)",
            (name,),
        ).fetchone()
        if existing is not None:
            raise ValueError("Player already exists.")
        cursor = conn.execute(
            "INSERT INTO players(display_name) VALUES (?)",
            (name,),
        )
        conn.commit()
        return int(cursor.lastrowid)


def leaderboard_rows(db_path: Path = DB_FILE) -> list[dict[str, Any]]:
    players = list_players(db_path)
    bootstrap_db(db_path)
    player_lookup = {player["display_name"].casefold(): player["display_name"] for player in players}

    with get_connection(db_path) as conn:
        frame_rows = conn.execute(
            """
            SELECT m.player1_name_snapshot, m.player2_name_snapshot, f.winner_name_snapshot
            FROM frames f
            JOIN matches m ON m.id = f.match_id
            WHERE f.winner_name_snapshot IS NOT NULL
            """
        ).fetchall()

    wins_by_name: dict[str, int] = {}
    played_by_name: dict[str, int] = {}
    for player1_name, player2_name, winner_name in frame_rows:
        for participant_name in [player1_name, player2_name]:
            if participant_name is None:
                continue
            canonical_name = player_lookup.get(participant_name.casefold())
            if canonical_name is not None:
                played_by_name[canonical_name] = played_by_name.get(canonical_name, 0) + 1

        canonical_winner = player_lookup.get(winner_name.casefold()) if winner_name is not None else None
        if canonical_winner is not None:
            wins_by_name[canonical_winner] = wins_by_name.get(canonical_winner, 0) + 1

    rows = []
    for player in players:
        rows.append(
            {
                "player": player["display_name"],
                "wins": wins_by_name.get(player["display_name"], 0),
                "played": played_by_name.get(player["display_name"], 0),
            }
        )
    return sorted(rows, key=lambda row: (-row["wins"], row["player"].lower(), row["player"]))
