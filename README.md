# RAG MCQ Agent

## Working
- Validate inputs, answer choices.
- Retrieve context using RAG
   - Get absolute path to textbook
   - Processes textbook into chunks and generates embeddings
      - Load textbook from file. Normalize whitespace but preserve structure
      - Chunk text into List of chunk dictionaries with text, start_char, end_char, chunk_index
      - Calculate SHA256 hash of textbook content to Verify textbook hasn't changed.
      - Peprocessing textbook
      - Chunking textbook
      - Generating embeddings
   - Retrieve top-k most relevant chunks for a query.
   - Build Prompt (Context, Few shots)
   - Call OpenAI API to get response for the question
   - Extract answer
      - CoT pattern matching (look for "Therefore", "Answer:", etc.)
      - Extract letter using regex (case-insensitive)
      - Extract number (0-3)
      - Fuzzy match - search for substrings matching answer choices

## Evaluation
The evaluation process is handled by [testbench.py](testbench.py), which reads questions, answer choices, and correct answers from [testbench.csv](data/testbench.csv). For each question, the agent predicts an answer by selecting from the provided options. The agent's response is compared to the correct choice, and a point is awarded for each correct match. The final score reflects the number of correct predictions out of the total number of questions.

All testbench run results are automatically stored in a PostgreSQL database. Each run is assigned a unique UUID, and results are stored with timestamps for historical analysis.


## Quick Start

### Using Docker (Recommended)

1. **Create `.env` file**:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```
   
   Optional: Configure PostgreSQL connection (defaults provided):
   ```bash
   echo "POSTGRES_DB=rag_mcq_agent" >> .env
   echo "POSTGRES_USER=rag_mcq_user" >> .env
   echo "POSTGRES_PASSWORD=rag_mcq_password" >> .env
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

2. **Set up API key and database**:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```
   
   For local PostgreSQL (if not using Docker):
   ```bash
   echo "POSTGRES_HOST=localhost" >> .env
   echo "POSTGRES_PORT=5432" >> .env
   echo "POSTGRES_DB=rag_mcq_agent" >> .env
   echo "POSTGRES_USER=your_db_user" >> .env
   echo "POSTGRES_PASSWORD=your_db_password" >> .env
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
python testbench.py
```

**Run with statistical validation** (for CI/CD):
```bash
python tests/run_tests_with_stats.py
```

### Programmatic Usage

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
- **PostgreSQL**: Included as a service in docker-compose, automatically starts with the application

### Database

The application uses PostgreSQL to store testbench results. When using Docker Compose, PostgreSQL is automatically configured and started. The database includes two tables:

- **`questions`**: Stores question data from the testbench CSV (id, question, answer choices, correct answer)
- **`runs`**: Stores individual question results for each testbench execution (run_id, question_id, user_response, is_correct, timestamp)

**Database Environment Variables**:
- `POSTGRES_HOST` (default: `postgres` in Docker, `localhost` locally)
- `POSTGRES_PORT` (default: `5432`)
- `POSTGRES_DB` (default: `rag_mcq_agent`)
- `POSTGRES_USER` (default: `rag_mcq_user`)
- `POSTGRES_PASSWORD` (default: `rag_mcq_password`)

Tables are automatically created on first run. Database data persists in a Docker volume (`postgres_data`).

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
│   ├── retriever.py   # RAG retrieval logic
│   └── prompts.py     # Prompt construction
├── data/              # Test data and textbook
│   ├── testbench.csv  # Sample questions
│   └── textbook.txt   # Reference textbook
├── tests/             # Test scripts
│   └── run_tests_with_stats.py  # Statistical test runner
├── app.py            # Streamlit web interface
├── testbench.py      # Evaluation script
├── hip_agent.py      # Main agent class
├── Dockerfile        # Docker configuration
└── requirements.txt  # Python dependencies
```

## Customization

The agent can be enhanced by modifying `hip_agent.py` while maintaining the `get_response(question, answer_choices)` interface.

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
