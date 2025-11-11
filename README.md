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
- **Web Interface**: Streamlit-based UI for CSV upload and interactive testing
- **Docker Support**: Fully containerized application ready for deployment

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

## Docker Deployment

The application is containerized and can be easily deployed using Docker.

### Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

### Quick Start with Script

The easiest way to get started:

```bash
# 1. Create .env file with your API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 2. Run the startup script
./start.sh
```

The script will automatically build and start the container, then display the URL to access the application.

### Option 1: Using Docker Compose (Recommended)

1. **Create a `.env` file** with your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

2. **Build and run the container**:
   ```bash
   docker compose up --build
   ```
   Or if using older Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

4. **Stop the container**:
   ```bash
   docker compose down
   ```

### Option 2: Using Docker CLI

1. **Build the Docker image**:
   ```bash
   docker build -t rag-mcq-agent .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name rag-mcq-agent \
     -p 8501:8501 \
     -e OPENAI_API_KEY=your-api-key-here \
     rag-mcq-agent
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

4. **View logs**:
   ```bash
   docker logs -f rag-mcq-agent
   ```

5. **Stop the container**:
   ```bash
   docker stop rag-mcq-agent
   docker rm rag-mcq-agent
   ```

### Docker Configuration

- **Port**: The application exposes port 8501 (Streamlit default)
- **Health Check**: Automatic health monitoring with 30-second intervals
- **Environment Variables**:
  - `OPENAI_API_KEY`: Your OpenAI API key (required)
- **Volumes**: Data directory is mounted read-only for access to testbench files

## How to Run

### Running the Testbench

To evaluate the agent on the sample questions:

```bash
python tests/testbench.py
```

This will:
1. Load questions from `data/testbench.csv`
2. Run the agent on each question
3. Compare answers against correct answers
4. Display the final score and detailed results

### Running with Statistical Validation

For CI/CD or more reliable results, use the statistical validation script:

```bash
python tests/run_tests_with_stats.py
```

This runs the testbench multiple times and validates using median score.

### Using the Web Interface

Launch the Streamlit web interface for an interactive testing experience:

```bash
streamlit run app.py
```

The web interface provides:
- CSV file upload for batch question processing
- Real-time progress tracking during evaluation
- Visual results display with color-coded correct/incorrect answers
- Detailed breakdown of each question with agent responses
- Score summary and statistics
- Option to filter results (all/correct/incorrect only)
- Export results as CSV
- Quick start with default testbench file

The interface will open in your browser at `http://localhost:8501`. You can upload any CSV file in the same format as `data/testbench.csv` or use the default testbench file.

### Using the Agent Programmatically

```python
from agent.hip_agent import HIPAgent

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

You can enhance the agent by modifying `agent/hip_agent.py` (or adding new files) as long as the interface to `tests/testbench.py` remains unchanged. The `HIPAgent` class must maintain the `get_response(question, answer_choices)` method signature.

### Potential Enhancements

- **Few-shot Learning**: Add example questions and answers to the prompt
- **Chain of Thought**: Encourage the model to reason through the problem
- **RAG Implementation**: Use embeddings and cosine similarity to retrieve relevant passages from `textbook.txt`
- **Web Search**: Integrate web search for additional context
- **Enhanced Frontend**: Add user authentication, question history, and performance analytics