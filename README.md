# RAG MCQ Agent

An intelligent Multiple Choice Question (MCQ) answering agent powered by Retrieval Augmented Generation (RAG) and GPT-3.5. Features a clean web interface for batch question processing and evaluation.

## Features

- **AI-Powered MCQ Answering**: Uses GPT-3.5 with advanced prompting techniques
- **RAG-Enhanced**: Retrieves relevant context from medical textbooks using embeddings
- **Web Interface**: Streamlit-based UI for CSV upload and interactive testing
- **Docker Support**: Fully containerized with optimized CPU-only PyTorch build
- **Automated Testing**: Statistical validation with testbench evaluation
- **Robust Parsing**: Multiple strategies to extract answers from model responses

## Quick Start

### Using Docker (Recommended)

1. **Create `.env` file**:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

2. **Start the application**:
   ```bash
   docker compose up --build
   ```

3. **Access the web interface**:
   Open `http://localhost:8501` in your browser

### Using Python

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key**:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Run the web interface**:
   ```bash
   streamlit run app.py
   ```

## Requirements

- Python 3.10+ (or Docker)
- OpenAI API key
- Dependencies: See `requirements.txt`

## Usage

### Web Interface

The Streamlit web interface provides:

- **CSV Upload**: Upload your own CSV file with MCQ questions
- **Default Testbench**: Quick start with pre-loaded test questions
- **Real-time Processing**: Progress tracking during evaluation
- **Results Dashboard**: Metrics, filtering, and detailed question analysis
- **Export Results**: Download results as CSV

**CSV Format**:
```csv
id,question,answer_0,answer_1,answer_2,answer_3,correct
1,"What is a GMO?","A genetically modified organism","A type of protein","A DNA sequence","None of the above","A genetically modified organism"
```

### Command Line Testing

**Run testbench**:
```bash
python tests/testbench.py
```

**Run with statistical validation** (for CI/CD):
```bash
python tests/run_tests_with_stats.py
```

### Programmatic Usage

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

## Docker Deployment

### Docker Compose

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Docker CLI

```bash
# Build image
docker build -t rag-mcq-agent .

# Run container
docker run -d \
  --name rag-mcq-agent \
  -p 8501:8501 \
  --env-file .env \
  rag-mcq-agent

# View logs
docker logs -f rag-mcq-agent

# Stop and remove
docker stop rag-mcq-agent && docker rm rag-mcq-agent
```

### Docker Configuration

- **Port**: 8501 (Streamlit default)
- **Health Check**: Automatic monitoring every 30 seconds
- **Environment**: `OPENAI_API_KEY` required (via `.env` file)
- **Image Size**: ~150MB (CPU-only PyTorch optimized)

## How It Works

1. **Question Processing**: Receives question and answer choices
2. **RAG Retrieval**: Retrieves relevant context from textbook using embeddings
3. **Prompt Construction**: Builds prompt with context, few-shot examples, and chain-of-thought reasoning
4. **API Call**: Sends to GPT-3.5-turbo via OpenAI API
5. **Answer Extraction**: Uses multiple parsing strategies (regex, fuzzy matching)
6. **Response**: Returns answer index (0-3) or -1 if no match

## Project Structure

```
rag-mcq-agent/
├── agent/              # Core agent implementation
│   ├── hip_agent.py   # Main agent class
│   ├── retriever.py   # RAG retrieval logic
│   └── prompts.py     # Prompt construction
├── data/              # Test data and textbook
│   ├── testbench.csv  # Sample questions
│   └── textbook.txt   # Reference textbook
├── tests/             # Test scripts
│   └── testbench.py  # Evaluation script
├── app.py            # Streamlit web interface
├── Dockerfile        # Docker configuration
└── requirements.txt  # Python dependencies
```

## Customization

The agent can be enhanced by modifying `agent/hip_agent.py` while maintaining the `get_response(question, answer_choices)` interface.

**Potential Enhancements**:
- Few-shot learning examples
- Chain-of-thought reasoning
- Enhanced RAG retrieval strategies
- Web search integration
- Performance analytics

## Testing

The project includes automated testing with statistical validation:

- **Threshold**: 70% accuracy (median score)
- **Runs**: 3 iterations for statistical reliability
- **CI/CD**: Integrated with GitHub Actions

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

## Security

⚠️ **Never commit your API key** to version control. The `.gitignore` file excludes `.env` and sensitive files.
