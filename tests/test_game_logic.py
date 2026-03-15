import sys
import pytest
from pathlib import Path

# Add parent directory to path so we can import logic_utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score


# ---------------------------------------------------------------------------
# Bug 1: Hint messages were swapped (Too High said "Go HIGHER", Too Low said "Go LOWER")
# ---------------------------------------------------------------------------

class TestBug1HintMessages:
    def test_too_high_outcome(self):
        outcome, _ = check_guess(60, 50)
        assert outcome == "Too High"

    def test_too_high_message_says_lower(self):
        # When guess is too high, player should be told to go LOWER
        _, message = check_guess(60, 50)
        assert "LOWER" in message.upper()

    def test_too_low_outcome(self):
        outcome, _ = check_guess(40, 50)
        assert outcome == "Too Low"

    def test_too_low_message_says_higher(self):
        # When guess is too low, player should be told to go HIGHER
        _, message = check_guess(40, 50)
        assert "HIGHER" in message.upper()

    def test_correct_guess_returns_win(self):
        outcome, _ = check_guess(50, 50)
        assert outcome == "Win"


# ---------------------------------------------------------------------------
# Bug 2: attempts counter initialized to 1 instead of 0 — caused off-by-one
# (attempt_number=0 on first guess should give full win points, not reduced)
# ---------------------------------------------------------------------------

class TestBug2AttemptsOffByOne:
    def test_first_attempt_win_score(self):
        # With fix: first guess increments attempts to 1 before scoring
        # 100 - 10 * (1 + 1) = 80
        score = update_score(0, "Win", 1)
        assert score == 80

    def test_bugged_first_attempt_would_give_less(self):
        # If bug was present, attempt_number=2 on first guess: 100 - 10*(2+1) = 70
        fixed = update_score(0, "Win", 1)
        bugged = update_score(0, "Win", 2)
        assert fixed > bugged


# ---------------------------------------------------------------------------
# Bug 3: Secret was cast to str on even attempts — broke integer comparison
# e.g. "9" > "10" is True lexicographically but 9 < 10 numerically
# ---------------------------------------------------------------------------

class TestBug3SecretStringCasting:
    def test_guess_below_two_digit_secret_is_too_low(self):
        # 9 < 10 numerically — must return Too Low, not Too High
        outcome, _ = check_guess(9, 10)
        assert outcome == "Too Low"

    def test_string_secret_raises_type_error(self):
        # Passing a string secret (as the bug did) now raises TypeError,
        # confirming the fixed code no longer accepts mixed types
        with pytest.raises(TypeError):
            check_guess(9, "10")

    def test_int_secret_gives_correct_result(self):
        outcome_fixed, _ = check_guess(9, 10)
        assert outcome_fixed == "Too Low"  # correct numeric comparison


# ---------------------------------------------------------------------------
# Bug 4: New Game always reset range to 1–100, ignoring difficulty
# ---------------------------------------------------------------------------

class TestBug4DifficultyRange:
    def test_easy_range(self):
        low, high = get_range_for_difficulty("Easy")
        assert (low, high) == (1, 20)

    def test_normal_range(self):
        low, high = get_range_for_difficulty("Normal")
        assert (low, high) == (1, 100)

    def test_hard_range(self):
        low, high = get_range_for_difficulty("Hard")
        assert (low, high) == (1, 50)

    def test_easy_high_is_not_100(self):
        # Before the fix, New Game always used randint(1, 100) regardless of difficulty
        _, high = get_range_for_difficulty("Easy")
        assert high != 100

    def test_hard_high_is_not_100(self):
        _, high = get_range_for_difficulty("Hard")
        assert high != 100
