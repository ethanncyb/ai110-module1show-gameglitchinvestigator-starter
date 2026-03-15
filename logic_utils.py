def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX Bug 1: Copilot flagged the hint logic as suspicious; closer inspection
    # (with ChatGPT) confirmed the messages were swapped — "Go HIGHER" was shown
    # when the guess was too high, and vice versa. Corrected the message strings.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def validate_guess_range(guess: int, low: int, high: int):
    """Return (ok, error_message). ok is False when guess is outside [low, high]."""
    if guess < low or guess > high:
        return False, f"Please enter a number between {low} and {high}."
    return True, None


# FEATURE: Claude Code (Agent mode) added format_history_entry to logic_utils.py
# as part of a multi-file feature expansion — keeping display-formatting logic
# out of app.py and testable in isolation.
def format_history_entry(guess: int, outcome: str) -> str:
    """Return a formatted string for one guess history row.

    Examples:
        format_history_entry(42, "Too High") -> "🔴 42 — Too High"
        format_history_entry(10, "Too Low")  -> "🔵 10 — Too Low"
        format_history_entry(25, "Win")      -> "🟢 25 — Win!"
    """
    icons = {"Win": "🟢", "Too High": "🔴", "Too Low": "🔵"}
    icon = icons.get(outcome, "⚪")
    label = "Win!" if outcome == "Win" else outcome
    return f"{icon} {guess} — {label}"
