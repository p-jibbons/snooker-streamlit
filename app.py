from copy import deepcopy

import streamlit as st

from snooker.game import BALL_VALUES, Ball, SnookerGame
from snooker.storage import (
    MATCH_FILE,
    SAVE_FILE,
    leaderboard_rows,
    list_players,
    load_game,
    load_match_state,
    record_completed_frame,
    register_player,
    save_game,
    save_match_state,
)

FOUL_VALUES = [4, 5, 6, 7]
BEST_OF_OPTIONS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]


def init_state():
    if "game" not in st.session_state:
        st.session_state.game = load_game() or SnookerGame()
    if "undo_stack" not in st.session_state:
        st.session_state.undo_stack = []
    if "match_state" not in st.session_state:
        st.session_state.match_state = load_match_state()
        st.session_state.match_state["player_names"] = st.session_state.game.player_names.copy()


def snapshot():
    return deepcopy(st.session_state.game)


def restore(state):
    st.session_state.game = state
    st.session_state.match_state["player_names"] = state.player_names.copy()
    save_game(st.session_state.game)
    save_match_state(st.session_state.match_state)


def push_undo():
    st.session_state.undo_stack.append(snapshot())


def set_player_names(p1: str, p2: str):
    game = st.session_state.game
    match_state = st.session_state.match_state
    new_names = [p1 or "Player 1", p2 or "Player 2"]
    changed = False
    if game.player_names != new_names:
        game.player_names = new_names
        changed = True
    if match_state["player_names"] != new_names:
        match_state["player_names"] = new_names
        changed = True
    if changed:
        save_game(game)
        save_match_state(match_state)


def apply_registered_player_selection(selected_p1: str, selected_p2: str, fallback_p1: str, fallback_p2: str):
    resolved_p1 = fallback_p1 if selected_p1 == "Custom name" else selected_p1
    resolved_p2 = fallback_p2 if selected_p2 == "Custom name" else selected_p2
    set_player_names(resolved_p1, resolved_p2)


def set_best_of(best_of: int):
    if st.session_state.match_state["best_of"] != best_of:
        st.session_state.match_state["best_of"] = best_of
        save_match_state(st.session_state.match_state)


def do_action(action, *args, **kwargs):
    push_undo()
    try:
        action(*args, **kwargs)
        save_game(st.session_state.game)
        st.rerun()
    except Exception as exc:
        st.session_state.undo_stack.pop()
        st.error(str(exc))


def undo():
    if st.session_state.undo_stack:
        restore(st.session_state.undo_stack.pop())


def add_registered_player(display_name: str):
    register_player(display_name)


def record_frame_winner(player_index: int):
    game = st.session_state.game
    match_state = st.session_state.match_state
    match_state["frames_won"][player_index] += 1
    frame_number = sum(match_state["frames_won"])
    winner_name = game.player_names[player_index]
    match_state.setdefault("frame_history", []).append(
        {
            "frame_number": frame_number,
            "winner_index": player_index,
            "winner_name": winner_name,
            "scores": game.scores.copy(),
        }
    )
    record_completed_frame(
        match_id=1,
        frame_number=frame_number,
        winner_player_slot=player_index + 1,
        winner_name_snapshot=winner_name,
        player1_score=game.scores[0],
        player2_score=game.scores[1],
        ended_by="clearance",
    )
    save_match_state(match_state)


def reset_frame(record_winner: bool = False):
    game = st.session_state.game
    winner = game.frame_winner()
    if record_winner and winner is not None:
        record_frame_winner(winner)
    push_undo()
    st.session_state.game = SnookerGame(player_names=game.player_names.copy())
    save_game(st.session_state.game)


def reset_match():
    game = st.session_state.game
    st.session_state.match_state = {
        "player_names": game.player_names.copy(),
        "frames_won": [0, 0],
        "best_of": st.session_state.match_state["best_of"],
        "frame_history": [],
    }
    save_match_state(st.session_state.match_state)


def frames_needed_to_win(best_of: int) -> int:
    return (best_of // 2) + 1


def match_summary() -> str:
    match_state = st.session_state.match_state
    target = frames_needed_to_win(match_state["best_of"])
    frames_won = match_state["frames_won"]
    names = match_state["player_names"]
    if frames_won[0] >= target:
        return f"Match point reached: {names[0]} wins the match {frames_won[0]}-{frames_won[1]}"
    if frames_won[1] >= target:
        return f"Match point reached: {names[1]} wins the match {frames_won[1]}-{frames_won[0]}"
    return f"Best of {match_state['best_of']} • First to {target} frames"


st.set_page_config(page_title="Snooker Scoreboard", page_icon="🎱", layout="wide")
init_state()
game: SnookerGame = st.session_state.game
match_state = st.session_state.match_state
registered_players = list_players()
leaderboard = leaderboard_rows()

st.markdown(
    "<h1 style='color: #cc3333; font-weight: 800; margin-bottom: 0.1rem;'>🎱 Snooker Scoreboard</h1>",
    unsafe_allow_html=True,
)
st.caption("Rule-aware snooker scoreboard with frame logic, local saves, lightweight match tracking, simple player registration, and registered-player assignment.")

with st.sidebar:
    st.header("Players")
    registered_options = [player["display_name"] for player in registered_players]
    player_options = registered_options + ["Custom name"]
    current_p1 = game.player_names[0] if game.player_names[0] in registered_options else "Custom name"
    current_p2 = game.player_names[1] if game.player_names[1] in registered_options else "Custom name"
    selected_p1 = st.selectbox("Player 1 source", player_options, index=player_options.index(current_p1))
    selected_p2 = st.selectbox("Player 2 source", player_options, index=player_options.index(current_p2))
    p1 = st.text_input("Player 1", value=game.player_names[0], disabled=selected_p1 != "Custom name")
    p2 = st.text_input("Player 2", value=game.player_names[1], disabled=selected_p2 != "Custom name")
    apply_registered_player_selection(selected_p1, selected_p2, p1, p2)

    st.caption(f"Registered players: {len(registered_players)}")
    if registered_players:
        st.caption(", ".join(player["display_name"] for player in registered_players))
    with st.form("register_player_form", clear_on_submit=True):
        new_player_name = st.text_input("Register player", placeholder="e.g. Paul")
        submitted = st.form_submit_button("Add player", use_container_width=True)
        if submitted:
            try:
                add_registered_player(new_player_name)
                st.success("Player registered")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    st.divider()
    st.header("Match")
    best_of = st.selectbox(
        "Match length",
        BEST_OF_OPTIONS,
        index=BEST_OF_OPTIONS.index(match_state.get("best_of", 1)),
    )
    set_best_of(best_of)
    if st.button("Reset match score", use_container_width=True):
        reset_match()

    st.divider()
    st.header("Frame controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Undo", use_container_width=True):
            undo()
    with col2:
        if st.button("Reset frame", use_container_width=True):
            reset_frame()

    if game.is_frame_over and game.frame_winner() is not None:
        if st.button("Start next frame + record winner", use_container_width=True):
            reset_frame(record_winner=True)
            st.rerun()

    st.divider()
    st.header("Save state")
    st.caption(f"Frame save: `{SAVE_FILE}`")
    st.caption(f"Match save: `{MATCH_FILE}`")
    if st.button("Save now", use_container_width=True):
        save_game(game)
        save_match_state(match_state)
        st.success("Frame and match saved")
    if st.button("Reload saved state", use_container_width=True):
        loaded_game = load_game()
        loaded_match = load_match_state()
        if loaded_game is None:
            st.warning("No saved frame found yet.")
        else:
            st.session_state.game = loaded_game
            loaded_match["player_names"] = loaded_game.player_names.copy()
            st.session_state.match_state = loaded_match
            st.session_state.undo_stack = []
            st.success("Saved frame and match reloaded")
            st.rerun()

    st.divider()
    st.header("Notes")
    st.caption("Tracks a standard two-player frame, including red/colour order, ordered clearance, re-spotted black, fouls, breaks, snookers-required pressure, local persistence, running match score, simple player registration, and registered-player assignment.")

st.subheader("Match score")
st.markdown(
    f"""
    <div style='display: flex; gap: 0.75rem; flex-wrap: nowrap; overflow-x: auto; margin-bottom: 0.75rem;'>
        <div style='flex: 1 1 0; min-width: 110px; border: 1px solid #e6e6e6; border-radius: 0.75rem; padding: 0.9rem 1rem; background: #fafafa;'>
            <div style='font-size: 0.9rem; color: #666;'>{match_state['player_names'][0]}</div>
            <div style='font-size: 2.1rem; font-weight: 800; line-height: 1.1;'>{match_state['frames_won'][0]}</div>
        </div>
        <div style='flex: 1 1 0; min-width: 110px; border: 1px solid #e6e6e6; border-radius: 0.75rem; padding: 0.9rem 1rem; background: #fafafa;'>
            <div style='font-size: 0.9rem; color: #666;'>{match_state['player_names'][1]}</div>
            <div style='font-size: 2.1rem; font-weight: 800; line-height: 1.1;'>{match_state['frames_won'][1]}</div>
        </div>
        <div style='flex: 1 1 0; min-width: 110px; border: 1px solid #dbeafe; border-radius: 0.75rem; padding: 0.9rem 1rem; background: #eff6ff;'>
            <div style='font-size: 0.9rem; color: #4b5563;'>Frames to win</div>
            <div style='font-size: 2.1rem; font-weight: 800; line-height: 1.1;'>{frames_needed_to_win(match_state['best_of'])}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.info(match_summary())

frame_history = match_state.get("frame_history", [])
if frame_history:
    st.caption("Completed frames")
    for frame in reversed(frame_history[-5:]):
        winner = frame["winner_name"]
        p1_score, p2_score = frame["scores"]
        st.write(f"- Frame {frame['frame_number']}: {winner} won {p1_score}-{p2_score}")

if leaderboard:
    st.subheader("Leaderboard")
    for idx, row in enumerate(leaderboard[:5], start=1):
        st.write(
            f"{idx}. {row['player']} — {row['wins']} frame win{'s' if row['wins'] != 1 else ''}"
            f" from {row['played']} recorded frame{'s' if row['played'] != 1 else ''}"
        )

current = game.current_player
other = 1 - current

score_cols = st.columns(2)
for idx, col in enumerate(score_cols):
    active = "✅ At table" if idx == current else ""
    with col:
        st.subheader(game.player_names[idx])
        st.metric("Frame score", game.scores[idx])
        st.caption(active)

info_cols = st.columns(4)
info_cols[0].metric("On", game.current_target_label())
info_cols[1].metric("Current break", game.current_break)
info_cols[2].metric("Reds left", game.reds_remaining)
info_cols[3].metric("Points remaining", game.points_remaining)

st.info(game.status_summary())

st.divider()
st.subheader("Legal scoring actions")

left, right = st.columns([2, 1])
with left:
    if Ball.RED in game.next_ball_on:
        red_cols = st.columns(4)
        for count, col in zip([1, 2, 3, 4], red_cols):
            disabled = count > game.reds_remaining
            with col:
                if st.button(f"Pot {count} red{'s' if count > 1 else ''}", use_container_width=True, disabled=disabled):
                    do_action(game.pot_red, count)
    else:
        choices = game.legal_colour_choices()
        colour_cols = st.columns(len(choices) or 1)
        for ball, col in zip(choices, colour_cols):
            with col:
                if st.button(f"{ball.value} +{BALL_VALUES[ball]}", use_container_width=True):
                    do_action(game.pot_colour, ball)

with right:
    st.markdown("**Turn management**")
    if st.button(f"Miss / end turn to {game.player_names[other]}", use_container_width=True, disabled=game.is_frame_over):
        do_action(game.miss)
    if game.needs_respotted_black():
        st.divider()
        st.caption("Scores are level after the colours. Start a one-ball shootout on the black.")
        if st.button("Start re-spotted black", use_container_width=True):
            do_action(game.start_respotted_black)

st.subheader("Fouls")
foul_cols = st.columns(len(FOUL_VALUES))
for points, col in zip(FOUL_VALUES, foul_cols):
    with col:
        if st.button(f"Foul +{points}", use_container_width=True, disabled=game.is_frame_over):
            do_action(game.foul, points, f"standard foul ({points})")

if game.on_respotted_black:
    st.caption("The frame is tied. The re-spotted black decides the winner: pot it to win, or concede 7 with a foul.")
elif game.phase.value == "reds_and_colours" and game.current_target_label() == "Any colour":
    st.caption("After potting a red, any one colour may be nominated. The app re-spots that colour automatically.")
elif game.phase.value == "colours_clearance":
    st.caption("Only the lowest remaining colour is on during the clearance phase.")

st.divider()
st.subheader("Recent history")
if game.history:
    for item in game.history[:20]:
        st.write(f"- {item}")
else:
    st.write("No actions yet.")
