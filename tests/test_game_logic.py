import sys
from pathlib import Path

import pytest

# Add parent directory to path so we can import logic_utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic_utils import (
    check_guess,
    format_history_entry,
    get_range_for_difficulty,
    parse_guess,
    update_score,
    validate_guess_range,
)


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


# ---------------------------------------------------------------------------
# Advanced Edge-Case Testing
# Generated with targeted Claude Code prompting:
#   "Write pytest edge cases for parse_guess covering non-numeric strings,
#    negative numbers, empty/None input, floats, and whitespace."
# ---------------------------------------------------------------------------

class TestParseGuessEdgeCases:
    def test_non_numeric_string_returns_error(self):
        # A word like "abc" must be rejected, not crash
        ok, value, err = parse_guess("abc")
        assert ok is False
        assert value is None
        assert err == "That is not a number."

    def test_special_characters_return_error(self):
        # Symbols should never be treated as a valid guess
        ok, value, err = parse_guess("!@#")
        assert ok is False
        assert err == "That is not a number."

    def test_empty_string_returns_error(self):
        # Submitting nothing should prompt the player to enter a guess
        ok, value, err = parse_guess("")
        assert ok is False
        assert err == "Enter a guess."

    def test_none_input_returns_error(self):
        # None (Streamlit default before any input) must be handled gracefully
        ok, value, err = parse_guess(None)
        assert ok is False
        assert err == "Enter a guess."

    def test_negative_number_is_parsed(self):
        # parse_guess should accept negative integers — range validation is the
        # caller's responsibility, not the parser's
        ok, value, err = parse_guess("-5")
        assert ok is True
        assert value == -5
        assert err is None

    def test_float_string_is_truncated_to_int(self):
        # "3.7" should parse to 3, not raise an error
        ok, value, err = parse_guess("3.7")
        assert ok is True
        assert value == 3
        assert err is None

    def test_whitespace_only_returns_error(self):
        # A guess of only spaces is not a valid number
        ok, value, err = parse_guess("   ")
        assert ok is False
        assert err == "That is not a number."

    def test_very_large_number_is_parsed(self):
        # No upper bound is enforced in the parser — large ints are valid input
        ok, value, err = parse_guess("999999")
        assert ok is True
        assert value == 999999


class TestCheckGuessEdgeCases:
    def test_guess_of_one_against_one(self):
        # Boundary: lowest possible value guessed correctly
        outcome, _ = check_guess(1, 1)
        assert outcome == "Win"

    def test_guess_just_above_secret(self):
        # Off-by-one above secret must be Too High, not Win
        outcome, _ = check_guess(51, 50)
        assert outcome == "Too High"

    def test_guess_just_below_secret(self):
        # Off-by-one below secret must be Too Low, not Win
        outcome, _ = check_guess(49, 50)
        assert outcome == "Too Low"


class TestUpdateScoreEdgeCases:
    def test_win_score_never_drops_below_10(self):
        # At attempt 10+, points formula goes negative — floor should clamp to 10
        score = update_score(0, "Win", 10)
        assert score >= 10

    def test_unknown_outcome_does_not_change_score(self):
        # Unrecognised outcome strings must be a no-op
        score = update_score(50, "Draw", 3)
        assert score == 50


# ---------------------------------------------------------------------------
# Feature: Guess History sidebar + High Score tracker
# format_history_entry lives in logic_utils.py so it can be tested independently
# ---------------------------------------------------------------------------

class TestFormatHistoryEntry:
    def test_too_high_uses_red_icon(self):
        entry = format_history_entry(42, "Too High")
        assert "🔴" in entry
        assert "42" in entry
        assert "Too High" in entry

    def test_too_low_uses_blue_icon(self):
        entry = format_history_entry(10, "Too Low")
        assert "🔵" in entry
        assert "10" in entry
        assert "Too Low" in entry

    def test_win_uses_green_icon(self):
        entry = format_history_entry(25, "Win")
        assert "🟢" in entry
        assert "25" in entry

    def test_unknown_outcome_uses_neutral_icon(self):
        entry = format_history_entry(7, "Draw")
        assert "⚪" in entry
        assert "7" in entry


class TestValidateGuessRange:
    def test_valid_guess_within_range(self):
        ok, err = validate_guess_range(10, 1, 20)
        assert ok is True
        assert err is None

    def test_guess_at_lower_boundary(self):
        ok, err = validate_guess_range(1, 1, 20)
        assert ok is True

    def test_guess_at_upper_boundary(self):
        ok, err = validate_guess_range(20, 1, 20)
        assert ok is True

    def test_guess_below_range(self):
        ok, err = validate_guess_range(0, 1, 20)
        assert ok is False
        assert "1" in err and "20" in err

    def test_guess_above_range(self):
        ok, err = validate_guess_range(21, 1, 20)
        assert ok is False
        assert "1" in err and "20" in err

    def test_error_message_mentions_both_bounds(self):
        _, err = validate_guess_range(99, 1, 50)
        assert "1" in err and "50" in err
