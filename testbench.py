import csv
from hip_agent import HIPAgent
from agent.config import MAX_PARALLEL_WORKERS

if __name__=="__main__":
    # Parse the CSV file
    with open("testbench.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        headers = next(reader)
        data = list(reader)

    # Get the correct answers and prepare questions
    correct_answers = []
    questions = []
    
    for row in data:
        answer_choices = [row[headers.index("answer_0")],
                        row[headers.index("answer_1")],
                        row[headers.index("answer_2")],
                        row[headers.index("answer_3")]]
        correct_answers.append(answer_choices.index(row[headers.index("correct")]))
        questions.append((row[headers.index("question")], answer_choices))

    # Instantiate a HIP agent
    agent = HIPAgent()

    # Process questions in parallel
    print(f"Processing {len(questions)} questions with {MAX_PARALLEL_WORKERS} parallel workers...")
    user_responses = agent.get_responses_batch(questions, max_workers=MAX_PARALLEL_WORKERS)

    # Calculate the score
    score = 0
    answers = []
    for i in range(len(data)):
        if user_responses[i] == correct_answers[i]:
            score += 1
            answers += [[1, user_responses[i], correct_answers[i]]]
        else:
            answers += [[0, user_responses[i], correct_answers[i]]]

    # Display the score
    print(f"Score:{score}/{len(data)}\n\n")
    print(answers)