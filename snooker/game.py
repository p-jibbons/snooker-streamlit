from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Ball(str, Enum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    BROWN = "Brown"
    BLUE = "Blue"
    PINK = "Pink"
    BLACK = "Black"


BALL_VALUES = {
    Ball.RED: 1,
    Ball.YELLOW: 2,
    Ball.GREEN: 3,
    Ball.BROWN: 4,
    Ball.BLUE: 5,
    Ball.PINK: 6,
    Ball.BLACK: 7,
}

COLOURS_IN_ORDER = [
    Ball.YELLOW,
    Ball.GREEN,
    Ball.BROWN,
    Ball.BLUE,
    Ball.PINK,
    Ball.BLACK,
]


class Phase(str, Enum):
    REDS_AND_COLOURS = "reds_and_colours"
    COLOURS_CLEARANCE = "colours_clearance"
    COMPLETE = "complete"


@dataclass
class ShotResult:
    description: str
    points_awarded: int = 0
    turn_ends: bool = False
    next_player: Optional[int] = None


@dataclass
class FoulResult(ShotResult):
    foul_points: int = 0


@dataclass
class SnookerGame:
    player_names: List[str] = field(default_factory=lambda: ["Player 1", "Player 2"])
    scores: List[int] = field(default_factory=lambda: [0, 0])
    current_player: int = 0
    current_break: int = 0
    reds_remaining: int = 15
    colours_cleared: List[Ball] = field(default_factory=list)
    expected_next: str = "red"
    on_respotted_black: bool = False
    history: List[str] = field(default_factory=list)

    @property
    def phase(self) -> Phase:
        if self.is_frame_over:
            return Phase.COMPLETE
        if self.reds_remaining > 0:
            return Phase.REDS_AND_COLOURS
        return Phase.COLOURS_CLEARANCE

    @property
    def is_frame_over(self) -> bool:
        if self.on_respotted_black:
            return False
        return self.reds_remaining == 0 and len(self.colours_cleared) == len(COLOURS_IN_ORDER)

    @property
    def player_on_name(self) -> str:
        return self.player_names[self.current_player]

    @property
    def opponent_index(self) -> int:
        return 1 - self.current_player

    @property
    def next_ball_on(self) -> List[Ball]:
        if self.is_frame_over:
            return []
        if self.on_respotted_black:
            return [Ball.BLACK]
        if self.reds_remaining > 0:
            if self.expected_next == "colour":
                return COLOURS_IN_ORDER.copy()
            return [Ball.RED]
        if self.expected_next == "colour":
            return COLOURS_IN_ORDER.copy()
        remaining = [ball for ball in COLOURS_IN_ORDER if ball not in self.colours_cleared]
        return [remaining[0]] if remaining else []

    @property
    def points_remaining(self) -> int:
        if self.phase == Phase.COMPLETE:
            return 0
        if self.on_respotted_black:
            return BALL_VALUES[Ball.BLACK]
        if self.phase == Phase.REDS_AND_COLOURS:
            colours_after_red = BALL_VALUES[Ball.BLACK] * self.reds_remaining
            reds = self.reds_remaining
            clearance = sum(BALL_VALUES[ball] for ball in COLOURS_IN_ORDER)
            if self.expected_next == "colour" and self.reds_remaining > 0:
                colours_after_red -= BALL_VALUES[Ball.BLACK]
            return reds + colours_after_red + clearance
        remaining = [ball for ball in COLOURS_IN_ORDER if ball not in self.colours_cleared]
        return sum(BALL_VALUES[ball] for ball in remaining)

    def lead(self) -> int:
        return abs(self.scores[0] - self.scores[1])

    def frame_winner(self) -> Optional[int]:
        if not self.is_frame_over:
            return None
        if self.scores[0] == self.scores[1]:
            return None
        return 0 if self.scores[0] > self.scores[1] else 1

    def needs_respotted_black(self) -> bool:
        return (
            not self.on_respotted_black
            and self.reds_remaining == 0
            and len(self.colours_cleared) == len(COLOURS_IN_ORDER)
            and self.scores[0] == self.scores[1]
        )

    def can_force_snookers(self) -> bool:
        return self.lead() > self.points_remaining

    def legal_colour_choices(self) -> List[Ball]:
        if self.phase == Phase.REDS_AND_COLOURS and self.expected_next == "colour":
            return COLOURS_IN_ORDER.copy()
        if self.phase == Phase.COLOURS_CLEARANCE:
            return self.next_ball_on
        return []

    def pot_red(self, count: int = 1) -> ShotResult:
        if self.phase != Phase.REDS_AND_COLOURS or self.expected_next != "red":
            raise ValueError("A red is not on.")
        if count < 1:
            raise ValueError("Must pot at least one red.")
        if count > self.reds_remaining:
            raise ValueError("Cannot pot more reds than remain.")

        points = count * BALL_VALUES[Ball.RED]
        self.reds_remaining -= count
        self.scores[self.current_player] += points
        self.current_break += points
        self.expected_next = "colour"
        description = f"{self.player_on_name} potted {count} red{'s' if count > 1 else ''} (+{points})"
        self.history.insert(0, description)
        return ShotResult(description=description, points_awarded=points)

    def pot_colour(self, ball: Ball) -> ShotResult:
        if ball == Ball.RED:
            raise ValueError("Use pot_red for reds.")
        if ball not in self.next_ball_on and not (
            self.phase == Phase.REDS_AND_COLOURS and self.expected_next == "colour"
        ):
            raise ValueError(f"{ball.value} is not on.")

        points = BALL_VALUES[ball]
        self.scores[self.current_player] += points
        self.current_break += points

        if self.on_respotted_black:
            self.on_respotted_black = False
            self.colours_cleared.append(Ball.BLACK)
            description = f"{self.player_on_name} potted the re-spotted Black (+{points})"
        elif self.reds_remaining > 0:
            self.expected_next = "red"
            description = f"{self.player_on_name} potted {ball.value} (+{points}) and it is re-spotted"
        elif self.expected_next == "colour":
            self.expected_next = "clearance"
            description = f"{self.player_on_name} potted {ball.value} (+{points}) and the colours now clear in order"
        else:
            self.colours_cleared.append(ball)
            description = f"{self.player_on_name} potted {ball.value} (+{points})"

        self.history.insert(0, description)
        return ShotResult(description=description, points_awarded=points)

    def miss(self) -> ShotResult:
        description = f"{self.player_on_name} missed"
        self.history.insert(0, description)
        self.end_turn()
        return ShotResult(
            description=description,
            turn_ends=True,
            next_player=self.current_player,
        )

    def start_respotted_black(self) -> ShotResult:
        if not self.needs_respotted_black():
            raise ValueError("A re-spotted black is not required.")
        self.on_respotted_black = True
        self.colours_cleared = [ball for ball in self.colours_cleared if ball != Ball.BLACK]
        self.expected_next = "clearance"
        self.current_break = 0
        description = "Frame tied — re-spotted Black started"
        self.history.insert(0, description)
        return ShotResult(description=description)

    def foul(self, foul_points: int, reason: str) -> FoulResult:
        if foul_points < 4:
            raise ValueError("Foul points must be at least 4.")
        self.scores[self.opponent_index] += foul_points
        offender = self.player_on_name
        opponent = self.player_names[self.opponent_index]
        was_respotted_black = self.on_respotted_black
        description = f"Foul by {offender}: {reason} (+{foul_points} to {opponent})"
        self.history.insert(0, description)
        self.end_turn()
        if was_respotted_black:
            self.on_respotted_black = False
            self.colours_cleared.append(Ball.BLACK)
        return FoulResult(
            description=description,
            foul_points=foul_points,
            turn_ends=True,
            next_player=self.current_player,
        )

    def end_turn(self) -> None:
        self.current_break = 0
        self.current_player = self.opponent_index
        if not self.on_respotted_black and self.reds_remaining > 0:
            self.expected_next = "red"

    def current_target_label(self) -> str:
        if self.phase == Phase.COMPLETE:
            return "Frame complete"
        if self.on_respotted_black:
            return "Respotted Black"
        if self.phase == Phase.REDS_AND_COLOURS:
            return "Red" if self.expected_next == "red" else "Any colour"
        return self.next_ball_on[0].value

    def status_summary(self) -> str:
        if self.is_frame_over:
            winner = self.frame_winner()
            if winner is None:
                return "Frame level."
            return f"Frame complete. Winner: {self.player_names[winner]}"
        if self.on_respotted_black:
            return f"On: Respotted Black • Next score wins • At table: {self.player_on_name}"
        pressure = "Snookers required" if self.can_force_snookers() else "Still enough points on the table"
        tie_note = " • Frame tied" if self.needs_respotted_black() else ""
        return f"On: {self.current_target_label()} • Reds left: {self.reds_remaining} • {pressure}{tie_note}"
