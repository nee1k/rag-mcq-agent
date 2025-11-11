import openai
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

class HIPAgent:
    def get_response(self, question, answer_choices):
        """
        Calls the OpenAI 3.5 API to generate a response to the question.
        The response is then matched to one of the answer choices and the index of the
        matching answer choice is returned. If the response does not match any answer choice,
        -1 is returned.

        Args:
            question: The question to be asked.
            answer_choices: A list of answer choices.

        Returns:
            The index of the answer choice that matches the response, or -1 if the response
            does not match any answer choice.
        """

        # Create the prompt with labeled answer choices.
        letters = ['A', 'B', 'C', 'D']
        answer_str = "\n".join([f"{letters[i]}) {choice}" for i, choice in enumerate(answer_choices)])
        prompt = f"{question}\n\n{answer_str}\n\nRespond with ONLY the letter of your answer choice (A, B, C, or D). Do not include any explanation."

        # Call the OpenAI 3.5 API.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        response_text = response.choices[0].message.content.strip()

        # Robust parsing: Try multiple strategies to extract the answer

        # Strategy 1: Extract letter using regex (case-insensitive)
        letter_match = re.search(r'\b([A-D])\b', response_text, re.IGNORECASE)
        if letter_match:
            letter = letter_match.group(1).upper()
            return ord(letter) - ord('A')  # Convert A→0, B→1, C→2, D→3

        # Strategy 2: Extract number (0-3)
        number_match = re.search(r'\b([0-3])\b', response_text)
        if number_match:
            return int(number_match.group(1))

        # Strategy 3: Fuzzy match - search for substrings matching answer choices
        response_lower = response_text.lower()
        for i, answer_choice in enumerate(answer_choices):
            if answer_choice.lower() in response_lower:
                return i

        # If no match found, return -1
        return -1
