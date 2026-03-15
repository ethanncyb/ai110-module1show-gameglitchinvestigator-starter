"""Game logic utilities for the Glitchy Guesser number-guessing game.

This module contains all pure game logic, separated from the Streamlit UI in
app.py. Keeping logic here makes every function independently unit-testable.

# DOCS: Copilot "Generate documentation" smart action was used as a starting
# point for all docstrings below; content was reviewed and expanded manually
# to include accurate Args/Returns/Raises details and concrete examples.
"""


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive (low, high) number range for a given difficulty.

    Difficulty levels and their ranges:
        - Easy:   1–20
        - Normal: 1–100
        - Hard:   1–50

    Any unrecognised difficulty string falls back to the Normal range (1–100).

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.

    Returns:
        A tuple ``(low, high)`` where both bounds are inclusive integers.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 50)
        >>> get_range_for_difficulty("Unknown")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str) -> tuple[bool, int | None, str | None]:
    """Parse raw text input from the user into a validated integer guess.

    Accepts whole numbers and decimal strings (decimals are truncated to int).
    Rejects ``None``, empty strings, whitespace-only strings, and non-numeric
    text without raising an exception.

    Args:
        raw: The raw string value from the Streamlit text input widget.
             May be ``None`` before the user has typed anything.

    Returns:
        A three-element tuple ``(ok, guess_int, error_message)``:

        - ``ok`` (bool): ``True`` when parsing succeeded.
        - ``guess_int`` (int | None): The parsed integer, or ``None`` on failure.
        - ``error_message`` (str | None): A human-readable error string when
          ``ok`` is ``False``, otherwise ``None``.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("3.7")
        (True, 3, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
        >>> parse_guess("")
        (False, None, 'Enter a guess.')
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


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a player's guess to the secret number and return the outcome.

    Both ``guess`` and ``secret`` must be integers. Passing a string for
    either argument will raise a ``TypeError`` on the ``>`` comparison.

    Args:
        guess:  The integer value the player guessed.
        secret: The hidden integer the player is trying to identify.

    Returns:
        A tuple ``(outcome, message)``:

        - ``outcome`` (str): One of ``"Win"``, ``"Too High"``, or ``"Too Low"``.
        - ``message`` (str): A short, emoji-prefixed hint shown to the player.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(40, 50)
        ('Too Low', '📈 Go HIGHER!')
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


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate and return an updated score based on the latest guess outcome.

    Scoring rules:
        - **Win**: awards ``100 - 10 * (attempt_number + 1)`` points, floored
          at a minimum of 10 so a late win still scores.
        - **Too High** on an even attempt: awards +5 (small bonus for guessing
          in the right half of the remaining range).
        - **Too High** on an odd attempt: deducts 5.
        - **Too Low**: always deducts 5.
        - Any other outcome: score is unchanged.

    Args:
        current_score:  The player's score before this guess.
        outcome:        The outcome string from :func:`check_guess` —
                        ``"Win"``, ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 1-based attempt count after the current guess.

    Returns:
        The new integer score after applying the outcome's point adjustment.

    Examples:
        >>> update_score(0, "Win", 1)
        80
        >>> update_score(100, "Too Low", 3)
        95
        >>> update_score(50, "Draw", 1)
        50
    """
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


def validate_guess_range(guess: int, low: int, high: int) -> tuple[bool, str | None]:
    """Check whether a parsed guess falls within the allowed difficulty range.

    This validation runs after :func:`parse_guess` succeeds and before the
    guess is processed by :func:`check_guess`, so out-of-range guesses are
    rejected without consuming an attempt.

    Args:
        guess: The integer guess to validate.
        low:   The inclusive lower bound of the allowed range.
        high:  The inclusive upper bound of the allowed range.

    Returns:
        A tuple ``(ok, error_message)``:

        - ``ok`` (bool): ``True`` when the guess is within ``[low, high]``.
        - ``error_message`` (str | None): A descriptive message when ``ok`` is
          ``False``, otherwise ``None``.

    Examples:
        >>> validate_guess_range(10, 1, 20)
        (True, None)
        >>> validate_guess_range(0, 1, 20)
        (False, 'Please enter a number between 1 and 20.')
        >>> validate_guess_range(21, 1, 20)
        (False, 'Please enter a number between 1 and 20.')
    """
    if guess < low or guess > high:
        return False, f"Please enter a number between {low} and {high}."
    return True, None


# FEATURE: Claude Code (Agent mode) added format_history_entry to logic_utils.py
# as part of a multi-file feature expansion — keeping display-formatting logic
# out of app.py and testable in isolation.
def format_history_entry(guess: int, outcome: str) -> str:
    """Format a single guess history record for display in the sidebar.

    Maps each outcome to a coloured circle emoji so the player can scan their
    guess history at a glance without reading every word.

    Outcome → icon mapping:
        - ``"Win"``      → 🟢
        - ``"Too High"`` → 🔴
        - ``"Too Low"``  → 🔵
        - anything else  → ⚪

    Args:
        guess:   The integer value the player guessed.
        outcome: The outcome string from :func:`check_guess`.

    Returns:
        A formatted string in the form ``"<icon> <guess> — <label>"``,
        for example ``"🔴 42 — Too High"`` or ``"🟢 25 — Win!"``.

    Examples:
        >>> format_history_entry(42, "Too High")
        '🔴 42 — Too High'
        >>> format_history_entry(10, "Too Low")
        '🔵 10 — Too Low'
        >>> format_history_entry(25, "Win")
        '🟢 25 — Win!'
    """
    icons = {"Win": "🟢", "Too High": "🔴", "Too Low": "🔵"}
    icon = icons.get(outcome, "⚪")
    label = "Win!" if outcome == "Win" else outcome
    return f"{icon} {guess} — {label}"
