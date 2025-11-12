#!/usr/bin/env python3
"""
Generate MCQ questions from textbook for testbench.csv expansion.

This script generates 80 additional questions (ids 21-100) from the Biology 2e
textbook to expand the testbench from 20 to 100 rows.
"""

import os
import sys
import csv
import re
import json
import random
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.textbook_processor import TextbookProcessor
from agent.utils.api_client import APIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QuestionGenerator:
    """Generates MCQ questions from textbook chunks using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the question generator.
        
        Args:
            api_key: OpenAI API key (if None, loads from environment)
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.api_client = APIClient(api_key)
        self.processor = None
        self.chunks = None
        
    def load_textbook_chunks(self, textbook_path: str) -> List[Dict]:
        """
        Load and chunk the textbook.
        
        Args:
            textbook_path: Path to textbook.txt file
            
        Returns:
            List of chunk dictionaries
        """
        print("Loading textbook and generating chunks...")
        self.processor = TextbookProcessor(textbook_path)
        chunks, _ = self.processor.process()
        self.chunks = chunks
        print(f"Loaded {len(chunks)} chunks from textbook")
        return chunks
    
    def sample_diverse_chunks(self, num_chunks: int, exclude_indices: List[int] = None) -> List[Dict]:
        """
        Sample diverse chunks evenly across the textbook.
        
        Args:
            num_chunks: Number of chunks to sample
            exclude_indices: Chunk indices to exclude (already used)
            
        Returns:
            List of sampled chunk dictionaries
        """
        if exclude_indices is None:
            exclude_indices = []
        
        total_chunks = len(self.chunks)
        available_indices = [i for i in range(total_chunks) if i not in exclude_indices]
        
        if len(available_indices) < num_chunks:
            print(f"Warning: Only {len(available_indices)} chunks available, requested {num_chunks}")
            num_chunks = len(available_indices)
        
        # Sample evenly across the textbook
        if num_chunks == 0:
            return []
        
        step = len(available_indices) / num_chunks
        sampled_indices = [available_indices[int(i * step)] for i in range(num_chunks)]
        
        # Add some randomness to avoid always picking same chunks
        random.shuffle(sampled_indices)
        
        sampled_chunks = [self.chunks[i] for i in sampled_indices]
        return sampled_chunks
    
    def create_generation_prompt(self, chunk_text: str) -> str:
        """
        Create prompt for generating MCQ question from textbook chunk.
        
        Args:
            chunk_text: Text content of the chunk
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert biology educator. Generate a multiple-choice question based on the following textbook passage.

Textbook Passage:
{chunk_text}

Generate a multiple-choice question that:
1. Tests understanding of key concepts from the passage
2. Has exactly 4 answer choices (A, B, C, D)
3. Has one clearly correct answer based on the passage
4. Has 3 plausible but incorrect distractors
5. Is appropriate for college-level biology students

Format your response as JSON:
{{
    "question": "The question text here",
    "answer_0": "First answer choice",
    "answer_1": "Second answer choice",
    "answer_2": "Third answer choice",
    "answer_3": "Fourth answer choice",
    "correct": "The correct answer text (must match one of answer_0 through answer_3)"
}}

Respond with ONLY valid JSON, no additional text or explanation."""
        
        return prompt
    
    def generate_question(self, chunk: Dict) -> Optional[Dict]:
        """
        Generate a single MCQ question from a chunk.
        
        Args:
            chunk: Chunk dictionary with 'text' key
            
        Returns:
            Question dictionary or None if generation failed
        """
        prompt = self.create_generation_prompt(chunk['text'])
        
        try:
            response = self.api_client.chat_completion(prompt)
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            question_data = self.parse_question_response(response_text)
            return question_data
            
        except Exception as e:
            print(f"Error generating question from chunk {chunk.get('chunk_index', 'unknown')}: {e}")
            return None
    
    def parse_question_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse LLM response to extract question data.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed question dictionary or None if parsing failed
        """
        # Try to extract JSON from response
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        try:
            # Try parsing as JSON
            data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['question', 'answer_0', 'answer_1', 'answer_2', 'answer_3', 'correct']
            if not all(field in data for field in required_fields):
                print(f"Missing required fields in response: {response_text[:200]}")
                return None
            
            # Validate correct answer matches one of the choices
            correct = data['correct']
            choices = [data['answer_0'], data['answer_1'], data['answer_2'], data['answer_3']]
            
            if correct not in choices:
                print(f"Correct answer '{correct}' does not match any choice")
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response: {response_text[:200]}")
            return None
    
    def generate_questions_batch(self, chunks: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Generate questions from chunks in batches with rate limiting.
        
        Args:
            chunks: List of chunk dictionaries
            batch_size: Number of questions to generate before pausing
            
        Returns:
            List of generated question dictionaries
        """
        questions = []
        used_chunk_indices = []
        
        print(f"\nGenerating questions from {len(chunks)} chunks...")
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} (chunk index {chunk.get('chunk_index', 'unknown')})...", end=" ")
            
            question = self.generate_question(chunk)
            
            if question:
                questions.append(question)
                used_chunk_indices.append(chunk.get('chunk_index'))
                print(f"✓ Generated question: {question['question'][:50]}...")
            else:
                print("✗ Failed to generate question")
            
            # Rate limiting: pause after each batch
            if (i + 1) % batch_size == 0:
                print(f"Pausing after batch of {batch_size} questions...")
                time.sleep(2)  # 2 second pause between batches
        
        print(f"\nSuccessfully generated {len(questions)} questions")
        return questions
    
    def append_to_csv(self, questions: List[Dict], csv_path: str, start_id: int = 21):
        """
        Append generated questions to testbench.csv.
        
        Args:
            questions: List of question dictionaries
            csv_path: Path to testbench.csv
            start_id: Starting ID for new questions
        """
        print(f"\nAppending {len(questions)} questions to {csv_path}...")
        
        # Read existing CSV to get current max ID
        existing_ids = []
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        existing_ids.append(int(row['id']))
                    except (ValueError, KeyError):
                        pass
        
        # Determine starting ID
        if existing_ids:
            max_id = max(existing_ids)
            start_id = max_id + 1
        
        # Append new questions
        with open(csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            for i, question in enumerate(questions):
                question_id = start_id + i
                row = [
                    question_id,
                    question['question'],
                    question['answer_0'],
                    question['answer_1'],
                    question['answer_2'],
                    question['answer_3'],
                    question['correct']
                ]
                writer.writerow(row)
        
        print(f"Successfully appended questions with IDs {start_id} to {start_id + len(questions) - 1}")


def main():
    """Main function to generate questions."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate MCQ questions from textbook')
    parser.add_argument('--num-questions', type=int, default=80,
                       help='Number of questions to generate (default: 80)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: generate only 5 questions')
    args = parser.parse_args()
    
    # Paths
    project_root = Path(__file__).parent.parent
    textbook_path = project_root / 'data' / 'textbook.txt'
    csv_path = project_root / 'data' / 'testbench.csv'
    
    # Configuration
    NUM_QUESTIONS_TO_GENERATE = 5 if args.test else args.num_questions
    
    print("=" * 60)
    print("Question Generation Script")
    print("=" * 60)
    print(f"Textbook: {textbook_path}")
    print(f"Output CSV: {csv_path}")
    print(f"Target: Generate {NUM_QUESTIONS_TO_GENERATE} questions")
    print("=" * 60)
    
    # Initialize generator
    try:
        generator = QuestionGenerator()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Load textbook chunks
    if not textbook_path.exists():
        print(f"Error: Textbook not found at {textbook_path}")
        sys.exit(1)
    
    generator.load_textbook_chunks(str(textbook_path))
    
    # Sample diverse chunks
    print(f"\nSampling {NUM_QUESTIONS_TO_GENERATE} diverse chunks...")
    sampled_chunks = generator.sample_diverse_chunks(NUM_QUESTIONS_TO_GENERATE)
    
    if len(sampled_chunks) < NUM_QUESTIONS_TO_GENERATE:
        print(f"Warning: Only sampled {len(sampled_chunks)} chunks")
    
    # Generate questions
    questions = generator.generate_questions_batch(sampled_chunks, batch_size=10)
    
    if not questions:
        print("Error: No questions were generated")
        sys.exit(1)
    
    # Append to CSV
    generator.append_to_csv(questions, str(csv_path))
    
    # Verify
    print(f"\nVerifying CSV...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        print(f"Total rows in CSV: {len(rows)} (including header)")
        print(f"Expected: {20 + len(questions)} rows (20 existing + {len(questions)} new)")
    
    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

