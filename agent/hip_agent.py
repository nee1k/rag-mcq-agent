from openai import AuthenticationError, BadRequestError
import os
from typing import List
from dotenv import load_dotenv
from .textbook_processor import TextbookProcessor
from .retriever import Retriever
from .prompts import (
    build_main_prompt,
    build_basic_prompt,
    format_context_section,
    format_few_shot_section,
    format_few_shot_examples
)
from .utils.api_client import APIClient
from .utils.answer_parser import AnswerParser
from .utils.validators import validate_question, validate_answer_choices
from .config import (
    RAG_SIMILARITY_THRESHOLD,
    RAG_TOP_K_RETRIEVE,
    RAG_TOP_K_USE
)

# Load environment variables from .env file
load_dotenv()

class HIPAgent:
    def __init__(self):
        """Initialize HIPAgent with lazy-loaded retriever."""
        self._retriever = None
        api_key = os.getenv("OPENAI_API_KEY")
        self.api_client = APIClient(api_key)
        self.answer_parser = AnswerParser()
    
    def _get_retriever(self):
        """Lazy initialize retriever on first use."""
        if self._retriever is None:
            try:
                # Get absolute path to textbook
                current_dir = os.path.dirname(os.path.abspath(__file__))
                textbook_path = os.path.join(current_dir, '..', 'data', 'textbook.txt')
                textbook_path = os.path.abspath(textbook_path)
                
                # Process textbook and create retriever
                processor = TextbookProcessor(textbook_path)
                chunks, embeddings = processor.process()
                self._retriever = Retriever(chunks, embeddings)
            except Exception as e:
                print(f"Warning: Could not initialize retriever: {e}. Continuing without RAG.")
                self._retriever = None
        return self._retriever
    
    def _retrieve_context(self, question: str) -> List[dict]:
        """
        Retrieve relevant context using RAG.
        
        Args:
            question: The question string
            
        Returns:
            List of relevant chunks
        """
        retrieved_chunks = []
        try:
            retriever = self._get_retriever()
            if retriever:
                chunks = retriever.retrieve_relevant_chunks(question, top_k=RAG_TOP_K_RETRIEVE)
                retrieved_chunks = [
                    chunk for chunk in chunks 
                    if chunk.get("similarity", 0) > RAG_SIMILARITY_THRESHOLD
                ]
        except Exception as e:
            print(f"Warning: RAG retrieval failed: {e}. Continuing without context.")
        return retrieved_chunks
    
    def _build_prompt(self, question: str, answer_choices: List[str], retrieved_chunks: List[dict]) -> str:
        """
        Build the complete prompt with context and few-shot examples.
        
        Args:
            question: The question string
            answer_choices: List of answer choices
            retrieved_chunks: List of retrieved context chunks
            
        Returns:
            Complete formatted prompt
        """
        context_section = format_context_section(retrieved_chunks, max_chunks=RAG_TOP_K_USE)
        few_shot_examples = format_few_shot_examples()
        examples_section = format_few_shot_section(few_shot_examples)
        
        return build_main_prompt(
            question=question,
            answer_choices=answer_choices,
            context_section=context_section,
            few_shot_section=examples_section
        )
    
    def _get_response_basic(self, question: str, answer_choices: List[str]) -> int:
        """Basic prompt without RAG/CoT/few-shot (fallback mode)."""
        prompt = build_basic_prompt(question, answer_choices)
        
        try:
            response = self.api_client.chat_completion(prompt)
            response_text = response.choices[0].message.content.strip()
            return self.answer_parser.extract_answer(response_text, answer_choices)
        except Exception as e:
            print(f"Error in basic mode: {e}")
            return -1
    
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
        # Validate inputs
        valid, error = validate_question(question)
        if not valid:
            print(f"Error: {error}")
            return -1
        
        valid, error = validate_answer_choices(answer_choices)
        if not valid:
            print(f"Error: {error}")
            return -1
        
        # Retrieve context using RAG
        retrieved_chunks = self._retrieve_context(question)
        
        # Build prompt
        prompt = self._build_prompt(question, answer_choices, retrieved_chunks)
        
        # Call the OpenAI API with retry logic
        try:
            response = self.api_client.chat_completion(prompt)
            response_text = response.choices[0].message.content.strip()
            
            # Extract answer using multiple strategies
            result = self.answer_parser.extract_answer(response_text, answer_choices)
            if result == -1:
                print(f"Warning: Could not parse answer. Falling back to basic mode.")
                return self._get_response_basic(question, answer_choices)
            return result
        except AuthenticationError as e:
            print(f"Error: Invalid API key. Please check your OPENAI_API_KEY environment variable.")
            return -1
        except BadRequestError as e:
            print(f"Error: Invalid request: {e}. Falling back to basic mode.")
            return self._get_response_basic(question, answer_choices)
        except Exception as e:
            print(f"Error: Unexpected error: {e}. Falling back to basic mode.")
            return self._get_response_basic(question, answer_choices)
