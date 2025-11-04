import openai

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

        # Create the prompt.
        answer_str = "\n".join(answer_choices)
        prompt = f"{question} \n\n{answer_str}"

        # Call the OpenAI 3.5 API.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        response_text = response.choices[0].message.content

        # Match the response to one of the answer choices.
        for i, answer_choice in enumerate(answer_choices):
            if response_text == answer_choice:
                return i

        # If the response does not match any answer choice, return -1.
        return -1
