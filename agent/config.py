"""Configuration constants for the agent."""

import os

# RAG Configuration
RAG_SIMILARITY_THRESHOLD = 0.3
RAG_TOP_K_RETRIEVE = 5
RAG_TOP_K_USE = 3

# API Configuration
OPENAI_MODEL = "gpt-3.5-turbo"
API_MAX_RETRIES = 3

# Parallel Processing Configuration
MAX_PARALLEL_WORKERS = 5  # Number of parallel workers for batch processing
PARALLEL_BATCH_SIZE = 10  # Batch size for parallel processing

# Answer Choices Configuration
MIN_CHOICES = 2
MAX_CHOICES = 4

# Web Search Configuration
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "false").lower() == "true"
WEB_SEARCH_PROVIDER = os.getenv("WEB_SEARCH_PROVIDER", "tavily")
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "3"))
WEB_SEARCH_MIN_RELEVANCE = float(os.getenv("WEB_SEARCH_MIN_RELEVANCE", "0.5"))
WEB_SEARCH_TIMEOUT = int(os.getenv("WEB_SEARCH_TIMEOUT", "10"))

