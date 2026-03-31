import pytest

from snooker.game import Ball, Phase, SnookerGame


def test_initial_state():
    game = SnookerGame(player_names=["A", "B"])
    assert game.phase == Phase.REDS_AND_COLOURS
    assert game.reds_remaining == 15
    assert game.next_ball_on == [Ball.RED]
    assert game.points_remaining == 147


def test_red_then_colour_then_red_flow():
    game = SnookerGame(player_names=["A", "B"])
    game.pot_red()
    assert game.scores == [1, 0]
    assert game.expected_next == "colour"
    game.pot_colour(Ball.BLACK)
    assert game.scores == [8, 0]
    assert game.expected_next == "red"
    assert game.reds_remaining == 14


def test_multiple_reds_are_legal_in_one_shot():
    game = SnookerGame(player_names=["A", "B"])
    game.pot_red(3)
    assert game.scores == [3, 0]
    assert game.reds_remaining == 12
    assert game.expected_next == "colour"


def test_cannot_pot_colour_when_red_is_on():
    game = SnookerGame(player_names=["A", "B"])
    with pytest.raises(ValueError):
        game.pot_colour(Ball.BLACK)


def test_colours_clearance_order_after_last_red_and_colour():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=1)
    game.pot_red()
    assert game.expected_next == "colour"
    game.pot_colour(Ball.BLUE)
    assert game.phase == Phase.COLOURS_CLEARANCE
    assert game.next_ball_on == [Ball.YELLOW]


def test_clearance_must_be_in_order():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red")
    with pytest.raises(ValueError):
        game.pot_colour(Ball.BLACK)
    game.pot_colour(Ball.YELLOW)
    assert game.next_ball_on == [Ball.GREEN]


def test_foul_awards_points_to_opponent_and_ends_turn():
    game = SnookerGame(player_names=["A", "B"])
    result = game.foul(4, "in-off")
    assert result.foul_points == 4
    assert game.scores == [0, 4]
    assert game.current_player == 1
    assert game.current_break == 0


def test_miss_ends_turn_without_points():
    game = SnookerGame(player_names=["A", "B"])
    game.pot_red()
    game.miss()
    assert game.current_player == 1
    assert game.current_break == 0
    assert game.scores == [1, 0]


def test_points_remaining_drops_during_clearance():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red")
    assert game.points_remaining == 27
    game.pot_colour(Ball.YELLOW)
    assert game.points_remaining == 25


def test_snookers_required_detection():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red", scores=[40, 0])
    assert game.points_remaining == 27
    assert game.can_force_snookers() is True


def test_frame_completion_and_winner():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red", scores=[20, 0])
    for ball in [Ball.YELLOW, Ball.GREEN, Ball.BROWN, Ball.BLUE, Ball.PINK, Ball.BLACK]:
        game.pot_colour(ball)
    assert game.is_frame_over is True
    assert game.frame_winner() == 0


def test_frame_level_on_all_balls_cleared_can_start_respotted_black():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red", scores=[0, 27])
    for ball in [Ball.YELLOW, Ball.GREEN, Ball.BROWN, Ball.BLUE, Ball.PINK, Ball.BLACK]:
        game.pot_colour(ball)
    assert game.needs_respotted_black() is True
    assert game.is_frame_over is True
    assert game.frame_winner() is None

    game.start_respotted_black()

    assert game.on_respotted_black is True
    assert game.is_frame_over is False
    assert game.next_ball_on == [Ball.BLACK]
    assert game.points_remaining == 7


def test_respotted_black_pot_decides_frame():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red", scores=[0, 27])
    for ball in [Ball.YELLOW, Ball.GREEN, Ball.BROWN, Ball.BLUE, Ball.PINK, Ball.BLACK]:
        game.pot_colour(ball)
    game.start_respotted_black()
    game.pot_colour(Ball.BLACK)

    assert game.is_frame_over is True
    assert game.frame_winner() == 0
    assert game.status_summary() == "Frame complete. Winner: A"


def test_respotted_black_foul_awards_frame_to_opponent():
    game = SnookerGame(player_names=["A", "B"], reds_remaining=0, expected_next="red", scores=[0, 27])
    for ball in [Ball.YELLOW, Ball.GREEN, Ball.BROWN, Ball.BLUE, Ball.PINK, Ball.BLACK]:
        game.pot_colour(ball)
    game.start_respotted_black()
    game.foul(7, "on the black")

    assert game.is_frame_over is True
    assert game.frame_winner() == 1
