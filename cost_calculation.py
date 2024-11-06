import re
from interfaces import Message

BASE_MESSAGE_COST = 1
MESSAGE_LENGTH_PENALTY_COST = 5
WORD_UNIQUINESS_DISCOUNT = 2

def calculate_word_cost(word: str) -> int:
    if not word:
        return 0

    word_length = len(word)

    if 1 <= word_length <= 3:
        word_cost = 0.1
        
    if 4 <= word_length <= 7:
        word_cost = 0.2

    if 8 <= word_length:
        word_cost = 0.3      

    if word_length >= 3:
        for every_third_char in word[2::3]:
            if every_third_char in {'a', 'e', 'i', 'o', 'u'}:
                word_cost += 0.3

    return word_cost

def is_palindrome(text: str) -> bool:
    alphanumeric_text = ''.join(char.lower() for char in text if char.isalnum())
    left_index = 0
    right_index = len(alphanumeric_text) - 1

    # faster than reversing string and checking for equality (and more space efficient)
    while left_index <= right_index:
        if not alphanumeric_text[left_index] == alphanumeric_text[right_index]:
            return False
        
        left_index += 1
        right_index -= 1

    return True

def calculate_message_cost(message: Message):
    # whitespaces are also represented by characters
    cost = len(message.text) + BASE_MESSAGE_COST

    word_counts = {}

    if len(message.text) > 100:
        cost += MESSAGE_LENGTH_PENALTY_COST

    # lowercase for easier palyndrome comparison
    lowercase_text = message.text.lower()
    for token in lowercase_text.split():
        word = "".join(re.findall(r"[a-zA-Z0-9'-]+", token))
        if not word:
            continue

        cost += calculate_word_cost(word)
        
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    if word_counts.values() and max(word_counts.values()) > 1:
        cost -= WORD_UNIQUINESS_DISCOUNT

    cost = cost if not is_palindrome(lowercase_text) else cost * 2

    return cost if cost >= 1 else BASE_MESSAGE_COST