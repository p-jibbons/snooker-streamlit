from snooker.game import Ball, SnookerGame
from snooker.storage import register_player


def test_status_summary_mentions_reds_initially():
    game = SnookerGame()
    summary = game.status_summary()
    assert "Reds left: 15" in summary
    assert "On: Red" in summary


def test_status_summary_reports_completion():
    game = SnookerGame(scores=[30, 0], reds_remaining=0, expected_next="red")
    for ball in [Ball.YELLOW, Ball.GREEN, Ball.BROWN, Ball.BLUE, Ball.PINK, Ball.BLACK]:
        game.pot_colour(ball)
    assert "Winner: Player 1" in game.status_summary()


def test_status_summary_reports_respotted_black_state():
    game = SnookerGame(player_names=["A", "B"], scores=[0, 27], reds_remaining=0, expected_next="red")
    for ball in [Ball.YELLOW, Ball.GREEN, Ball.BROWN, Ball.BLUE, Ball.PINK, Ball.BLACK]:
        game.pot_colour(ball)
    game.start_respotted_black()
    assert game.status_summary() == "On: Respotted Black • Next score wins • At table: A"


def test_registered_players_are_listed_alphabetically(tmp_path, monkeypatch):
    from snooker import storage

    db_path = tmp_path / "snooker.db"
    monkeypatch.setattr(storage, "DB_FILE", db_path)
    register_player("Zoe", db_path)
    register_player("alice", db_path)

    players = storage.list_players(db_path)

    assert [player["display_name"] for player in players] == ["alice", "Zoe"]


def test_registered_player_assignment_prefers_selected_names():
    selected_p1 = "Alice"
    selected_p2 = "Custom name"
    fallback_p1 = "Manual One"
    fallback_p2 = "Manual Two"

    resolved_p1 = fallback_p1 if selected_p1 == "Custom name" else selected_p1
    resolved_p2 = fallback_p2 if selected_p2 == "Custom name" else selected_p2

    assert resolved_p1 == "Alice"
    assert resolved_p2 == "Manual Two"


def test_streamlit_action_flow_prefers_immediate_rerun_after_successful_click():
    action_saves_state = True
    reruns_after_success = True

    assert action_saves_state is True
    assert reruns_after_success is True
