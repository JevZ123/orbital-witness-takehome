from cost_calculation import (
    get_word,
    is_palindrome,
    calculate_word_cost,
    calculate_text_cost,
    PALINDROME_COST_MULTIPLIER,
    WORD_COST_LOW,
    WORD_COST_MEDIUM,
    WORD_COST_HIGH,
    THIRD_VOWEL_COST,
    BASE_MESSAGE_COST,
    BASE_CHARACTER_COST,
    MESSAGE_LENGTH_PENALTY_COST,
    WORD_UNIQUINESS_DISCOUNT,
)
import unittest
from unittest.mock import patch


class TestCostCalculations(unittest.TestCase):

    def test_is_palindrome(self):

        self.assertTrue(is_palindrome("a"))
        self.assertTrue(is_palindrome("aa"))
        self.assertTrue(is_palindrome("aaa"))
        self.assertTrue(is_palindrome("aaaa"))
        self.assertTrue(is_palindrome("aba"))
        self.assertTrue(is_palindrome("ab)a!"))
        self.assertTrue(is_palindrome("abba"))

        self.assertFalse(is_palindrome(""))
        self.assertFalse(is_palindrome("aaaba"))
        self.assertFalse(is_palindrome("ab"))

    def test_word_cost(self):
        self.assertEqual(calculate_word_cost(""), 0)

        self.assertEqual(calculate_word_cost("b"), WORD_COST_LOW)
        self.assertEqual(calculate_word_cost("bbb"), WORD_COST_LOW)
        self.assertEqual(calculate_word_cost("bba"), WORD_COST_LOW + THIRD_VOWEL_COST)

        self.assertEqual(calculate_word_cost("bbbb"), WORD_COST_MEDIUM)
        self.assertEqual(calculate_word_cost("bbbbbbb"), WORD_COST_MEDIUM)
        self.assertEqual(
            calculate_word_cost("bbabbab"), WORD_COST_MEDIUM + THIRD_VOWEL_COST * 2
        )

        self.assertEqual(calculate_word_cost("bbbbbbbb"), WORD_COST_HIGH)
        self.assertEqual(calculate_word_cost("bbbbbbbbbbbbbbbbbbbbb"), WORD_COST_HIGH)

    def test_get_word(self):
        self.assertEqual(get_word("a"), "a")
        self.assertEqual(get_word("a1"), "a")
        self.assertEqual(get_word("a1!*&^"), "a")
        self.assertEqual(get_word("a'"), "a'")
        self.assertEqual(get_word("a'-"), "a'-")

    def test_calculate_text_cost(self):
        with patch("cost_calculation.calculate_word_cost", return_value=0):
            with patch("cost_calculation.is_palindrome", return_value=False):
                self.assertEqual(calculate_text_cost(""), BASE_MESSAGE_COST)
                self.assertEqual(
                    calculate_text_cost("a a"),
                    BASE_MESSAGE_COST + BASE_CHARACTER_COST * 3,
                )
                self.assertEqual(
                    calculate_text_cost("a" * 100),
                    BASE_MESSAGE_COST
                    + BASE_CHARACTER_COST * 100
                    - WORD_UNIQUINESS_DISCOUNT,
                )
                self.assertEqual(
                    calculate_text_cost("a" * 101),
                    BASE_MESSAGE_COST
                    + BASE_CHARACTER_COST * 101
                    + MESSAGE_LENGTH_PENALTY_COST
                    - WORD_UNIQUINESS_DISCOUNT,
                )

                self.assertEqual(
                    calculate_text_cost("a" * 20 + " " + "a" * 20),
                    BASE_MESSAGE_COST + BASE_CHARACTER_COST * 41,
                )

            with patch("cost_calculation.is_palindrome", return_value=True):
                self.assertEqual(
                    calculate_text_cost("a a"),
                    (BASE_MESSAGE_COST + BASE_CHARACTER_COST * 3)
                    * PALINDROME_COST_MULTIPLIER,
                )

        with patch("cost_calculation.calculate_word_cost", return_value=-100):
            self.assertEqual(calculate_text_cost("a a"), BASE_MESSAGE_COST)
