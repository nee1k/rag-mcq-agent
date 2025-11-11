#!/usr/bin/env python3
"""
Run testbench multiple times and validate using statistical measures.
Exits with code 0 if median score meets threshold, otherwise exits with code 1.
"""
import subprocess
import re
import sys
import statistics
from typing import List

def extract_score(output: str) -> tuple[int, int]:
    """Extract score and total from testbench output."""
    # Pattern: Score:15/20
    match = re.search(r'Score:(\d+)/(\d+)', output)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError(f"Could not extract score from output: {output[:200]}")

def run_testbench() -> tuple[int, int]:
    """Run testbench once and return the (score, total) tuple."""
    result = subprocess.run(
        ['python', 'testbench.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running testbench:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    return extract_score(result.stdout)

def main():
    num_runs = 3
    threshold_percentage = 0.70  # 70% threshold (can be adjusted)
    
    print(f"Running testbench {num_runs} times...\n")
    
    scores: List[int] = []
    total_questions = None
    
    # Run testbench multiple times
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...", end=" ", flush=True)
        score, total = run_testbench()
        
        # Set total_questions from first run
        if total_questions is None:
            total_questions = total
        
        # Verify total is consistent across runs
        if total != total_questions:
            print(f"\nWarning: Total questions mismatch! Expected {total_questions}, got {total}", file=sys.stderr)
        
        scores.append(score)
        print(f"Score: {score}/{total_questions}")
    
    # Calculate threshold based on percentage
    threshold = int(total_questions * threshold_percentage)
    
    print(f"\nThreshold: median score >= {threshold}/{total_questions} ({threshold_percentage*100:.0f}%)")
    
    # Calculate statistics
    median_score = statistics.median(scores)
    avg_score = statistics.mean(scores)
    min_score = min(scores)
    max_score = max(scores)
    
    print("\n" + "="*50)
    print("STATISTICAL SUMMARY")
    print("="*50)
    print(f"Runs: {num_runs}")
    print(f"Scores: {scores}")
    print(f"Minimum: {min_score}/{total_questions}")
    print(f"Maximum: {max_score}/{total_questions}")
    print(f"Average: {avg_score:.2f}/{total_questions}")
    print(f"Median:  {median_score}/{total_questions}")
    print(f"Threshold: {threshold}/{total_questions} ({threshold_percentage*100:.0f}%)")
    print("="*50)
    
    # Validate using median
    if median_score >= threshold:
        print(f"✅ PASS: Median score ({median_score}/{total_questions}) meets threshold ({threshold}/{total_questions})")
        sys.exit(0)
    else:
        print(f"❌ FAIL: Median score ({median_score}/{total_questions}) below threshold ({threshold}/{total_questions})")
        sys.exit(1)

if __name__ == "__main__":
    main()

