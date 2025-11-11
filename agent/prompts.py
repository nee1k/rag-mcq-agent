"""Prompt templates and formatting utilities for HIPAgent."""

from typing import List


# Few-shot examples demonstrating reasoning process
FEW_SHOT_EXAMPLES = [
    {
        "question": "GMOs are created by ________",
        "choices": [
            "generating genomic DNA fragments with restriction endonucleases",
            "introducing recombinant DNA into an organism by any means",
            "overexpressing proteins in E. coli",
            "all of the above"
        ],
        "reasoning": "GMOs are defined by introducing recombinant DNA (B). Option A is a technique, not the definition. Option C is about protein production. Option D is incorrect.",
        "answer": "B"
    },
    {
        "question": "Which scientific concept did Charles Darwin and Alfred Wallace independently discover?",
        "choices": [
            "mutation",
            "natural selection",
            "overbreeding",
            "sexual reproduction"
        ],
        "reasoning": "Both Darwin and Wallace independently developed the theory of natural selection (B). Mutation was discovered later. Overbreeding and sexual reproduction were known concepts before their time.",
        "answer": "B"
    },
    {
        "question": "Which situation would most likely lead to allopatric speciation?",
        "choices": [
            "Flood causes the formation of a new lake",
            "A storm causes several large trees to fall down",
            "A mutation causes a new trait to develop",
            "An injury"
        ],
        "reasoning": "Allopatric speciation requires geographic isolation. A new lake creates a geographic barrier separating populations (A). A storm is temporary. A mutation describes sympatric speciation. An injury affects an individual, not a population.",
        "answer": "A"
    }
]


class PromptTemplates:
    """Centralized prompt templates for the HIP agent."""
    
    SYSTEM_ROLE = "You are an expert biology tutor. Answer the following multiple-choice question accurately."
    
    CONTEXT_HEADER = "=== Relevant Textbook Information ==="
    CONTEXT_FOOTER = "=== End of Textbook Information ==="
    
    FEW_SHOT_INTRO = "Here are examples of how to approach similar questions:"
    
    INSTRUCTIONS = """Instructions:
1. Read the textbook information carefully (if provided above)
2. Identify key concepts from the textbook that directly relate to the question
3. Evaluate each answer choice against the textbook information
4. Use your biological knowledge to support your reasoning
5. Choose the most accurate answer"""
    
    RESPONSE_FORMAT = """Format your response as:
Reasoning: [your step-by-step analysis referencing textbook information when relevant]
Answer: [LETTER]"""
    
    BASIC_INSTRUCTION = "Respond with ONLY the letter (A, B, C, or D)."


def format_answer_choices(answer_choices: List[str]) -> str:
    """
    Format answer choices as labeled options.
    
    Args:
        answer_choices: List of answer choice strings
        
    Returns:
        Formatted string with A-D labels
    """
    letters = ['A', 'B', 'C', 'D']
    return "\n".join([f"{letters[i]}) {choice}" for i, choice in enumerate(answer_choices)])


def format_context_section(retrieved_chunks: List[dict], max_chunks: int = 3) -> str:
    """
    Format retrieved RAG context chunks into a context section.
    
    Args:
        retrieved_chunks: List of chunk dictionaries with 'text' key
        max_chunks: Maximum number of chunks to include
        
    Returns:
        Formatted context section string, or empty string if no chunks
    """
    if not retrieved_chunks:
        return ""
    
    context_texts = []
    for i, chunk in enumerate(retrieved_chunks[:max_chunks], 1):
        context_texts.append(f"[Context {i}]\n{chunk['text']}")
    
    context_body = "\n".join(context_texts)
    return f"""{PromptTemplates.CONTEXT_HEADER}
{context_body}
{PromptTemplates.CONTEXT_FOOTER}

"""


def format_few_shot_examples(examples: List[dict] = None) -> str:
    """
    Format few-shot examples for the prompt.
    
    Args:
        examples: List of example dictionaries. If None, uses default FEW_SHOT_EXAMPLES.
        
    Returns:
        Formatted few-shot examples string
    """
    if examples is None:
        examples = FEW_SHOT_EXAMPLES
    
    examples_text = []
    letters = ['A', 'B', 'C', 'D']
    
    for i, example in enumerate(examples, 1):
        choices_text = "\n".join([
            f"{letters[j]}) {choice}" 
            for j, choice in enumerate(example["choices"])
        ])
        
        example_text = f"""Example {i}:
Question: {example["question"]}
Answer choices:
{choices_text}

Reasoning: {example["reasoning"]}
Answer: {example["answer"]}"""
        examples_text.append(example_text)
    
    return "\n\n".join(examples_text)


def format_few_shot_section(few_shot_examples: str) -> str:
    """
    Format few-shot examples section.
    
    Args:
        few_shot_examples: Pre-formatted few-shot examples string
        
    Returns:
        Formatted few-shot section
    """
    return f"""{PromptTemplates.FEW_SHOT_INTRO}

{few_shot_examples}

"""


def build_main_prompt(
    question: str,
    answer_choices: List[str],
    context_section: str = "",
    few_shot_section: str = ""
) -> str:
    """
    Build the main prompt for the agent.
    
    Args:
        question: The question text
        answer_choices: List of answer choice strings
        context_section: Formatted RAG context section (optional)
        few_shot_section: Formatted few-shot examples section (optional)
        
    Returns:
        Complete formatted prompt string
    """
    answer_str = format_answer_choices(answer_choices)
    
    prompt_parts = [
        PromptTemplates.SYSTEM_ROLE,
        "",
        context_section,
        few_shot_section,
        "Now answer this NEW question:",
        "",
        f"Question: {question}",
        "",
        "Answer choices:",
        answer_str,
        "",
        PromptTemplates.INSTRUCTIONS,
        "",
        PromptTemplates.RESPONSE_FORMAT
    ]
    
    return "\n".join(prompt_parts)


def build_basic_prompt(question: str, answer_choices: List[str]) -> str:
    """
    Build a basic prompt without RAG/CoT/few-shot (fallback mode).
    
    Args:
        question: The question text
        answer_choices: List of answer choice strings
        
    Returns:
        Simple formatted prompt string
    """
    answer_str = format_answer_choices(answer_choices)
    return f"{question}\n\n{answer_str}\n\n{PromptTemplates.BASIC_INSTRUCTION}"

