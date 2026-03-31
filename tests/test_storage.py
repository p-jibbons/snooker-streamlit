import sqlite3
from pathlib import Path

from snooker.game import Ball, SnookerGame
from snooker.storage import (
    bootstrap_db,
    get_connection,
    leaderboard_rows,
    list_players,
    load_game,
    load_match_state,
    record_completed_frame,
    register_player,
    save_game,
    save_match_state,
)


def test_save_and_load_roundtrip(tmp_path: Path):
    path = tmp_path / "frame.json"
    db_path = tmp_path / "snooker.db"
    game = SnookerGame(player_names=["Paul", "Guest"])
    game.pot_red(2)
    game.pot_colour(Ball.BLACK)
    game.foul(4, "in-off")

    save_game(game, path, db_path)
    restored = load_game(path, db_path)

    assert restored is not None
    assert restored.player_names == game.player_names
    assert restored.scores == game.scores
    assert restored.current_player == game.current_player
    assert restored.current_break == game.current_break
    assert restored.reds_remaining == game.reds_remaining
    assert restored.expected_next == game.expected_next
    assert restored.history == game.history


def test_load_missing_file_returns_none(tmp_path: Path):
    path = tmp_path / "missing.json"
    db_path = tmp_path / "snooker.db"
    assert load_game(path, db_path) is None


def test_match_state_defaults_when_missing(tmp_path: Path):
    path = tmp_path / "match.json"
    db_path = tmp_path / "snooker.db"
    match_state = load_match_state(path, db_path)
    assert match_state == {
        "player_names": ["Player 1", "Player 2"],
        "frames_won": [0, 0],
        "best_of": 1,
        "frame_history": [],
    }


def test_save_and_load_match_state_roundtrip(tmp_path: Path):
    path = tmp_path / "match.json"
    db_path = tmp_path / "snooker.db"
    match_state = {
        "player_names": ["Paul", "Guest"],
        "frames_won": [2, 1],
        "best_of": 5,
        "frame_history": [
            {
                "frame_number": 1,
                "winner_index": 0,
                "winner_name": "Paul",
                "scores": [68, 44],
            }
        ],
    }

    save_match_state(match_state, path, db_path)
    restored = load_match_state(path, db_path)

    assert restored == match_state


def test_bootstrap_db_creates_expected_tables(tmp_path: Path):
    db_path = tmp_path / "snooker.db"
    bootstrap_db(db_path)

    with get_connection(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        }

    assert {"app_state", "matches", "frames", "players"}.issubset(tables)


def test_save_game_writes_sql_app_state(tmp_path: Path):
    json_path = tmp_path / "frame.json"
    db_path = tmp_path / "snooker.db"
    game = SnookerGame(player_names=["Paul", "Guest"])
    game.pot_red()

    save_game(game, json_path, db_path)

    with get_connection(db_path) as conn:
        row = conn.execute("SELECT value_json FROM app_state WHERE key = 'current_frame'").fetchone()

    assert row is not None
    assert '"reds_remaining": 14' in row[0]


def test_save_match_state_writes_sql_app_state(tmp_path: Path):
    json_path = tmp_path / "match.json"
    db_path = tmp_path / "snooker.db"
    match_state = {
        "player_names": ["Paul", "Guest"],
        "frames_won": [1, 0],
        "best_of": 3,
        "frame_history": [],
    }

    save_match_state(match_state, json_path, db_path)

    with get_connection(db_path) as conn:
        row = conn.execute("SELECT value_json FROM app_state WHERE key = 'current_match'").fetchone()

    assert row is not None
    assert '"best_of": 3' in row[0]


def test_load_game_falls_back_to_json_when_sql_state_missing(tmp_path: Path):
    json_path = tmp_path / "frame.json"
    db_path = tmp_path / "snooker.db"
    game = SnookerGame(player_names=["Paul", "Guest"])
    game.pot_red(2)

    save_game(game, json_path, db_path)

    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM app_state WHERE key = 'current_frame'")
        conn.commit()

    restored = load_game(json_path, db_path)

    assert restored is not None
    assert restored.player_names == ["Paul", "Guest"]
    assert restored.reds_remaining == 13
    assert restored.scores == [2, 0]


def test_load_match_state_falls_back_to_json_when_sql_state_missing(tmp_path: Path):
    json_path = tmp_path / "match.json"
    db_path = tmp_path / "snooker.db"
    match_state = {
        "player_names": ["Paul", "Guest"],
        "frames_won": [1, 2],
        "best_of": 5,
        "frame_history": [
            {
                "frame_number": 1,
                "winner_index": 1,
                "winner_name": "Guest",
                "scores": [41, 67],
            }
        ],
    }

    save_match_state(match_state, json_path, db_path)

    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM app_state WHERE key = 'current_match'")
        conn.commit()

    restored = load_match_state(json_path, db_path)

    assert restored == match_state


def test_bootstrap_db_is_idempotent(tmp_path: Path):
    db_path = tmp_path / "snooker.db"

    first = bootstrap_db(db_path)
    second = bootstrap_db(db_path)

    assert first == db_path
    assert second == db_path

    with get_connection(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        }

    assert {"app_state", "matches", "frames", "players"}.issubset(tables)


def test_record_completed_frame_inserts_relational_history_row(tmp_path: Path):
    db_path = tmp_path / "snooker.db"
    frame_id = record_completed_frame(
        match_id=1,
        frame_number=2,
        winner_player_slot=1,
        winner_name_snapshot="Paul",
        player1_score=74,
        player2_score=38,
        ended_by="clearance",
        db_path=db_path,
    )

    assert frame_id >= 1

    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT match_id, frame_number, winner_player_slot, winner_name_snapshot,
                   player1_score, player2_score, ended_by
            FROM frames
            WHERE id = ?
            """,
            (frame_id,),
        ).fetchone()

    assert row == (1, 2, 1, "Paul", 74, 38, "clearance")


def test_register_player_persists_and_lists_players(tmp_path: Path):
    db_path = tmp_path / "snooker.db"

    player_id = register_player("Paul", db_path)
    players = list_players(db_path)

    assert player_id >= 1
    assert len(players) == 1
    assert players[0]["display_name"] == "Paul"
    assert players[0]["is_active"] is True


def test_register_player_rejects_case_insensitive_duplicates(tmp_path: Path):
    db_path = tmp_path / "snooker.db"

    register_player("Paul", db_path)

    try:
        register_player("paul", db_path)
        assert False, "Expected duplicate player registration to fail"
    except ValueError as exc:
        assert str(exc) == "Player already exists."


def test_four_registered_users_are_listed_cleanly(tmp_path: Path):
    db_path = tmp_path / "snooker.db"

    for name in ["Paul", "Alice", "Bob", "Dana"]:
        register_player(name, db_path)

    players = list_players(db_path)

    assert len(players) == 4
    assert [player["display_name"] for player in players] == ["Alice", "Bob", "Dana", "Paul"]
    assert len({player["id"] for player in players}) == 4


def test_leaderboard_rows_rank_players_by_recorded_frame_wins(tmp_path: Path):
    db_path = tmp_path / "snooker.db"

    for name in ["Paul", "Alice", "Bob"]:
        register_player(name, db_path)

    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO matches(id, player1_name_snapshot, player2_name_snapshot, best_of)
            VALUES (1, 'Paul', 'Alice', 3), (2, 'Paul', 'Bob', 1)
            """
        )
        conn.commit()

    record_completed_frame(1, 1, 1, "Paul", 74, 10, "clearance", db_path)
    record_completed_frame(1, 2, 2, "Alice", 20, 64, "clearance", db_path)
    record_completed_frame(2, 1, 1, "Paul", 71, 40, "clearance", db_path)

    rows = leaderboard_rows(db_path)

    assert rows == [
        {"player": "Paul", "wins": 2, "played": 3},
        {"player": "Alice", "wins": 1, "played": 2},
        {"player": "Bob", "wins": 0, "played": 1},
    ]
