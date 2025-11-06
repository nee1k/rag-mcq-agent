# Hippocratic AI Coding Assignment

A multiple-choice question answering system using GPT-3.5.

## Project Structure

```
hippocratic_takehome/
├── src/                    # Source code
│   ├── __init__.py
│   ├── hip_agent.py       # Main agent implementation
│   └── testbench.py       # Test runner (do not modify)
├── data/                   # Data files
│   ├── testbench.csv      # Question and answer data
│   └── textbook.txt       # Reference textbook
├── logs/                   # Log files
├── k8s/                    # Kubernetes deployment files
├── Dockerfile              # Container configuration
└── requirements.txt        # Python dependencies
```

## Prerequisites

- Python 3.11+
- OpenAI API key
- pip

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hippocratic_takehome
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```
   
   Or export it in your shell:
   ```bash
   export OPENAI_API_KEY=your-api-key-here
   ```

## Running the Project

### Local Execution

Run the testbench to evaluate the agent on the test questions:

```bash
python src/testbench.py
```

This will:
- Load questions from `data/testbench.csv`
- Run the HIPAgent on each question
- Display the final score and detailed results

### Docker Execution

Build the Docker image:

```bash
docker build -t hippocratic-agent .
```

Run the container:

```bash
docker run --env-file .env hippocratic-agent
```

Or pass the API key directly:

```bash
docker run -e OPENAI_API_KEY=your-api-key-here hippocratic-agent
```

### Kubernetes Deployment

See the [k8s/README.md](k8s/README.md) for Kubernetes deployment instructions.

## Development

- **Source code**: Modify `src/hip_agent.py` to improve the agent's performance
- **Test data**: Questions are in `data/testbench.csv`
- **Reference material**: The textbook is available in `data/textbook.txt`

**Important**: Do not modify `src/testbench.py` as it is the evaluation interface.

## Configuration

- **OpenAI Model**: The agent uses GPT-3.5-turbo (as specified in the assignment)
- **OpenAI SDK Version**: 0.27.8

## For Assignment Details

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the full assignment requirements and evaluation criteria.

