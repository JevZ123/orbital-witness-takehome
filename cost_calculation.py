import re
from interfaces import Message

BASE_MESSAGE_COST = 1
BASE_CHARACTER_COST = 0.05
MESSAGE_LENGTH_PENALTY_COST = 5
WORD_UNIQUINESS_DISCOUNT = 2
WORD_COST_LOW = 0.1
WORD_COST_MEDIUM = 0.2
WORD_COST_HIGH = 0.3
THIRD_VOWEL_COST = 0.3
PALINDROME_COST_MULTIPLIER = 2


def get_word(potential_word: str):
    return "".join(re.findall(r"[a-z'-]+", potential_word))


def calculate_word_cost(word: str) -> int:

    if not word:
        return 0

    word_length = len(word)

    if 1 <= word_length <= 3:
        word_cost = WORD_COST_LOW

    if 4 <= word_length <= 7:
        word_cost = WORD_COST_MEDIUM

    if 8 <= word_length:
        word_cost = WORD_COST_HIGH

    if word_length >= 3:
        for every_third_char in word[2::3]:
            if every_third_char in {"a", "e", "i", "o", "u"}:
                word_cost += THIRD_VOWEL_COST

    return word_cost


def is_palindrome(text: str) -> bool:
    if not text:
        return False

    alphanumeric_text = "".join(char.lower() for char in text if char.isalnum())
    left_index = 0
    right_index = len(alphanumeric_text) - 1

    # faster than reversing string and checking for equality (and more space efficient)
    while left_index <= right_index:
        if not alphanumeric_text[left_index] == alphanumeric_text[right_index]:
            return False

        left_index += 1
        right_index -= 1

    return True


def calculate_text_cost(text: str):
    # whitespaces are also represented by characters
    cost = len(text) * BASE_CHARACTER_COST + BASE_MESSAGE_COST

    word_counts = {}

    if len(text) > 100:
        cost += MESSAGE_LENGTH_PENALTY_COST

    # lowercase for easier palyndrome comparison
    lowercase_text = text.lower()
    for token in lowercase_text.split():
        word = get_word(token)
        cost += calculate_word_cost(word)

        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    if word_counts.values() and max(word_counts.values()) == 1:
        cost -= WORD_UNIQUINESS_DISCOUNT

    cost = (
        cost if not is_palindrome(lowercase_text) else cost * PALINDROME_COST_MULTIPLIER
    )

    return cost if cost >= 1 else BASE_MESSAGE_COST
