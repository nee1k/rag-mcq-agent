#!/usr/bin/env python3
"""
Benchmarking script to measure accuracy and latency metrics.
Runs extended_testbench.csv and writes results to a CSV file.
"""

import csv
import time
from datetime import datetime
from typing import List, Dict
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from hip_agent_v0 import HIPAgent


def run_benchmark(testbench_path: str, output_path: str = None) -> Dict:
    """
    Run benchmark on testbench CSV file.
    
    Args:
        testbench_path: Path to testbench CSV file
        output_path: Path to output CSV file (optional)
        
    Returns:
        Dictionary with summary metrics
    """
    print(f"Loading testbench from: {testbench_path}")
    
    # Parse the CSV file
    with open(testbench_path, "r", encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        headers = next(reader)
        data = list(reader)
    
    print(f"Found {len(data)} questions")
    print("Initializing agent...")
    
    # Instantiate HIP agent (this will load embeddings on first use)
    agent_init_start = time.time()
    agent = HIPAgent()
    agent_init_time = time.time() - agent_init_start
    print(f"Agent initialized in {agent_init_time:.2f}s")
    
    # Prepare results
    results = []
    correct_answers = []
    total_start_time = time.time()
    
    print("\nProcessing questions...")
    for idx, row in enumerate(data, 1):
        question_id = row[headers.index("id")]
        question = row[headers.index("question")]
        answer_choices = [
            row[headers.index("answer_0")],
            row[headers.index("answer_1")],
            row[headers.index("answer_2")],
            row[headers.index("answer_3")]
        ]
        correct_answer_text = row[headers.index("correct")]
        correct_answer_idx = answer_choices.index(correct_answer_text)
        correct_answers.append(correct_answer_idx)
        
        # Measure latency for this question
        question_start = time.time()
        response_idx = agent.get_response(question, answer_choices)
        question_latency = time.time() - question_start
        
        is_correct = response_idx == correct_answer_idx
        
        results.append({
            'question_id': question_id,
            'question': question,
            'correct_answer_idx': correct_answer_idx,
            'agent_response_idx': response_idx,
            'is_correct': is_correct,
            'latency_seconds': question_latency
        })
        
        # Progress indicator
        if idx % 10 == 0:
            print(f"  Processed {idx}/{len(data)} questions...")
    
    total_time = time.time() - total_start_time
    
    # Calculate metrics
    total_questions = len(results)
    correct_count = sum(1 for r in results if r['is_correct'])
    accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Latency statistics
    latencies = [r['latency_seconds'] for r in results]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    median_latency = sorted(latencies)[len(latencies) // 2] if latencies else 0
    
    # Summary metrics
    summary = {
        'total_questions': total_questions,
        'correct_count': correct_count,
        'accuracy_percentage': accuracy,
        'total_time_seconds': total_time,
        'avg_latency_seconds': avg_latency,
        'min_latency_seconds': min_latency,
        'max_latency_seconds': max_latency,
        'median_latency_seconds': median_latency,
        'agent_init_time_seconds': agent_init_time,
        'questions_per_second': total_questions / total_time if total_time > 0 else 0
    }
    
    # Write detailed results to CSV
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"benchmark_results_{timestamp}.csv"
    
    print(f"\nWriting results to: {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'question_id', 'question', 'correct_answer_idx', 
            'agent_response_idx', 'is_correct', 'latency_seconds'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Write summary metrics to separate file
    summary_path = output_path.replace('.csv', '_summary.csv')
    print(f"Writing summary to: {summary_path}")
    with open(summary_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"Total Questions:        {total_questions}")
    print(f"Correct Answers:        {correct_count}")
    print(f"Accuracy:               {accuracy:.2f}%")
    print(f"Total Time:             {total_time:.2f}s")
    print(f"Agent Init Time:        {agent_init_time:.2f}s")
    print(f"Questions/Second:       {summary['questions_per_second']:.2f}")
    print(f"\nLatency Statistics:")
    print(f"  Average:              {avg_latency:.2f}s")
    print(f"  Median:                {median_latency:.2f}s")
    print(f"  Min:                   {min_latency:.2f}s")
    print(f"  Max:                   {max_latency:.2f}s")
    print("="*60)
    
    return summary


if __name__ == "__main__":
    import argparse
    
    # Get parent directory for default paths
    script_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    parser = argparse.ArgumentParser(description='Benchmark HIP Agent performance')
    parser.add_argument(
        '--testbench', 
        type=str, 
        default=os.path.join(script_parent_dir, 'data', 'extended_testbench.csv'),
        help='Path to testbench CSV file (default: data/extended_testbench.csv)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=None,
        help='Path to output CSV file (default: benchmark_results_TIMESTAMP.csv)'
    )
    
    args = parser.parse_args()
    
    # Check if testbench file exists
    if not os.path.exists(args.testbench):
        print(f"Error: Testbench file not found: {args.testbench}")
        sys.exit(1)
    
    # Run benchmark
    try:
        summary = run_benchmark(args.testbench, args.output)
    except Exception as e:
        print(f"Error during benchmarking: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

