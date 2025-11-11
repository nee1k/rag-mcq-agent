# RAG MCQ Agent

A Retrieval Augmented Generation (RAG) based Multiple Choice Question (MCQ) answering agent. This project uses GPT-3.5 to answer multiple-choice questions, with support for retrieval-augmented generation using a reference textbook.

## Overview

This project implements an intelligent agent that can answer multiple-choice questions by leveraging OpenAI's GPT-3.5 model. The agent is designed to be enhanced with various techniques such as:
- Few-shot prompting
- Chain of thought reasoning
- Retrieval Augmented Generation (RAG) using embeddings and cosine similarity
- Web search integration

## Features

- **MCQ Answering**: Answers multiple-choice questions using GPT-3.5-turbo
- **Robust Parsing**: Multiple strategies to extract answers from model responses
- **Testbench Evaluation**: Automated scoring system to evaluate agent performance
- **RAG Support**: Infrastructure for retrieval-augmented generation (textbook included)

## Requirements

- Python 3.x
- OpenAI API key
- Dependencies listed in `requirements.txt`:
  - `openai==0.27.8`
  - `python-dotenv`

## Setup

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd rag-mcq-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   
   Option A: Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```
   
   Option B: Place your API key in `openaikey.txt` (if using that method)
   
   **⚠️ Important**: Never commit your API key to version control. The `.gitignore` file is configured to exclude API keys and sensitive files.

## How to Run

### Running the Testbench

To evaluate the agent on the sample questions:

```bash
python testbench.py
```

This will:
1. Load questions from `testbench.csv`
2. Run the agent on each question
3. Compare answers against correct answers
4. Display the final score and detailed results

### Using the Agent Programmatically

```python
from hip_agent import HIPAgent

agent = HIPAgent()
question = "What is a GMO?"
answer_choices = [
    "A genetically modified organism",
    "A type of protein",
    "A DNA sequence",
    "None of the above"
]
response_index = agent.get_response(question, answer_choices)
print(f"Answer index: {response_index}")
```

## How It Works

1. **Question Processing**: The agent receives a question and multiple answer choices (A, B, C, D)
2. **Prompt Construction**: Creates a formatted prompt with labeled answer choices
3. **API Call**: Sends the prompt to GPT-3.5-turbo via OpenAI API
4. **Answer Extraction**: Uses multiple parsing strategies to extract the answer:
   - Regex matching for letters (A-D)
   - Number extraction (0-3)
   - Fuzzy matching against answer choices
5. **Response**: Returns the index of the selected answer (0-3) or -1 if no match found

## Customization

You can enhance the agent by modifying `hip_agent.py` (or adding new files) as long as the interface to `testbench.py` remains unchanged. The `HIPAgent` class must maintain the `get_response(question, answer_choices)` method signature.

### Potential Enhancements

- **Few-shot Learning**: Add example questions and answers to the prompt
- **Chain of Thought**: Encourage the model to reason through the problem
- **RAG Implementation**: Use embeddings and cosine similarity to retrieve relevant passages from `textbook.txt`
- **Web Search**: Integrate web search for additional context
- **Frontend**: Build a web interface for interactive question answering