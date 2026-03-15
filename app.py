import random

import streamlit as st

# REFACTOR: Copilot (Agent mode) identified that all game logic was mixed into app.py;
# Claude Code extracted get_range_for_difficulty, parse_guess, check_guess, and
# update_score into logic_utils.py to separate UI from business logic.
# FEATURE: Claude Code (Agent mode) orchestrated adding format_history_entry to
# logic_utils.py and wiring the Guess History sidebar + High Score tracker here
# in app.py — a coordinated two-file change driven by a single Agent prompt.
from logic_utils import (
    check_guess,
    format_history_entry,
    get_range_for_difficulty,
    parse_guess,
    update_score,
    validate_guess_range,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX Bug 2: Copilot spotted that attempts was initialized to 1 instead of 0,
# causing an off-by-one error where players got one fewer guess than allowed.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# FEATURE: guess_log stores (guess, outcome) tuples for the sidebar display.
# high_score persists across new games so the player can chase their best run.
if "guess_log" not in st.session_state:
    st.session_state.guess_log = []

if "high_score" not in st.session_state:
    st.session_state.high_score = 0

# Reset the game whenever the player switches difficulty so the secret
# is always within the new range and the attempt limit is correct.
if st.session_state.get("last_difficulty") != difficulty:
    st.session_state.last_difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_log = []

st.subheader("Make a guess")

# Placeholder filled after the submit handler so attempts reflects the
# post-increment value — avoids the off-by-one caused by top-down rendering.
attempts_info = st.empty()

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

if "enter_pressed" not in st.session_state:
    st.session_state.enter_pressed = False


def _on_guess_change():
    # on_change fires when the user edits the field and presses Enter,
    # which triggers a rerun — treat it the same as clicking Submit Guess.
    st.session_state.enter_pressed = True


raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}",
    on_change=_on_guess_change,
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    # FIX Bug 4: Claude Code identified that the original reset used hardcoded
    # randint(1, 100), ignoring the selected difficulty range.
    st.session_state.secret = random.randint(low, high)
    # FIX Bug 5: Claude Code found that score, status, and history were never
    # cleared on new game, leaving the app stuck in a won/lost state.
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_log = []  # reset per-game log; high_score is kept
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    # Render sidebar here before st.stop() so history and high score
    # remain visible after the game ends (st.stop() skips the bottom panels).
    st.sidebar.divider()
    st.sidebar.subheader("🏆 High Score")
    st.sidebar.metric("Best score this session", st.session_state.high_score)
    st.sidebar.divider()
    st.sidebar.subheader("📋 Guess History")
    if st.session_state.guess_log:
        for entry in reversed(st.session_state.guess_log):
            st.sidebar.caption(format_history_entry(entry[0], entry[1]))
    else:
        st.sidebar.caption("No guesses yet.")
    st.stop()

if submit or st.session_state.enter_pressed:
    st.session_state.enter_pressed = False  # consume the flag
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        # Invalid input: show error but do NOT consume an attempt
        st.error(err)
    else:
        in_range, range_err = validate_guess_range(guess_int, low, high)
        if not in_range:
            # Out-of-range guess: show error but do NOT consume an attempt
            st.error(range_err)
        else:
            st.session_state.attempts += 1
            st.session_state.history.append(guess_int)

            # FIX Bug 3: Claude Code removed the parity check that cast the secret to
            # a string on even attempts, which broke numeric comparison (e.g. "9" > "10"
            # lexicographically but 9 < 10 numerically).
            secret = st.session_state.secret

            outcome, message = check_guess(guess_int, secret)

            if show_hint:
                st.warning(message)

            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )

            # FEATURE: log each valid guess with its outcome for the sidebar history
            st.session_state.guess_log.append((guess_int, outcome))

            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                # FEATURE: update high score if this win beat the previous best
                if st.session_state.score > st.session_state.high_score:
                    st.session_state.high_score = st.session_state.score
                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
            else:
                if st.session_state.attempts >= attempt_limit:
                    st.session_state.status = "lost"
                    st.error(
                        f"Out of attempts! "
                        f"The secret was {st.session_state.secret}. "
                        f"Score: {st.session_state.score}"
                    )

attempts_info.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

# Sidebar panels placed here so guess_log and high_score reflect the current
# submit's result before rendering (Streamlit renders top-to-bottom per rerun).
st.sidebar.divider()
st.sidebar.subheader("🏆 High Score")
st.sidebar.metric("Best score this session", st.session_state.high_score)

st.sidebar.divider()
st.sidebar.subheader("📋 Guess History")
if st.session_state.guess_log:
    for entry in reversed(st.session_state.guess_log):
        st.sidebar.caption(format_history_entry(entry[0], entry[1]))
else:
    st.sidebar.caption("No guesses yet.")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
