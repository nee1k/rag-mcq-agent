"""Prompt templates and formatting utilities for HIPAgent."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


class PromptsConfigurationError(Exception):
    """Raised when prompts configuration file cannot be loaded or is invalid."""
    pass

# Cached prompts data
_cached_prompts: Optional[Dict] = None


def _load_prompts_from_file() -> Dict:
    """
    Load prompt templates from YAML file.
    
    Checks PROMPTS_FILE environment variable first, then falls back to
    agent/prompts.yaml relative to this module's location.
    
    Returns:
        Dictionary with 'few_shot_examples' and 'templates' keys
        
    Raises:
        PromptsConfigurationError: If PyYAML is not installed, file is not found,
            YAML is invalid, or required keys are missing
    """
    if yaml is None:
        raise PromptsConfigurationError(
            "PyYAML is not installed. Install it with: pip install pyyaml"
        )
    
    # Determine file path
    prompts_file = os.getenv("PROMPTS_FILE")
    if prompts_file:
        file_path = Path(prompts_file)
    else:
        # Default to prompts.yaml in the same directory as this module
        module_dir = Path(__file__).parent
        file_path = module_dir / "prompts.yaml"
    
    # Check if file exists
    if not file_path.exists():
        raise PromptsConfigurationError(
            f"Prompts configuration file not found: {file_path}. "
            f"Please create the file or set PROMPTS_FILE environment variable to point to a valid prompts file."
        )
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate structure
        if not isinstance(data, dict):
            raise PromptsConfigurationError(
                f"Invalid YAML structure in {file_path}: root must be a dictionary"
            )
        
        if "few_shot_examples" not in data or "templates" not in data:
            raise PromptsConfigurationError(
                f"Invalid YAML structure in {file_path}: missing required keys. "
                f"Expected 'few_shot_examples' and 'templates' at root level."
            )
        
        logger.info(f"Successfully loaded prompts from {file_path}")
        return data
    
    except yaml.YAMLError as e:
        raise PromptsConfigurationError(
            f"Error parsing YAML file {file_path}: {e}"
        ) from e
    except PromptsConfigurationError:
        raise
    except Exception as e:
        raise PromptsConfigurationError(
            f"Error reading prompts file {file_path}: {e}"
        ) from e


def _get_prompts() -> Dict:
    """
    Get prompts data, loading from file on first call (cached).
    
    Returns:
        Dictionary with 'few_shot_examples' and 'templates' keys
        
    Raises:
        PromptsConfigurationError: If prompts file cannot be loaded
    """
    global _cached_prompts
    
    if _cached_prompts is None:
        _cached_prompts = _load_prompts_from_file()
    
    return _cached_prompts


# Public API: FEW_SHOT_EXAMPLES (maintains backward compatibility)
def _get_few_shot_examples() -> List[dict]:
    """Get few-shot examples from loaded configuration."""
    return _get_prompts()["few_shot_examples"]


# For backward compatibility, expose as a list that's dynamically loaded
class _FewShotExamplesList:
    """Wrapper to maintain backward compatibility with FEW_SHOT_EXAMPLES list access."""
    
    def __iter__(self):
        return iter(_get_few_shot_examples())
    
    def __getitem__(self, index):
        return _get_few_shot_examples()[index]
    
    def __len__(self):
        return len(_get_few_shot_examples())


FEW_SHOT_EXAMPLES = _FewShotExamplesList()


class _TemplateDescriptor:
    """Descriptor for accessing template values dynamically."""
    
    def __init__(self, key: str):
        self.key = key
    
    def __get__(self, obj, objtype=None):
        return _get_prompts()["templates"].get(self.key, "")


class PromptTemplates:
    """Centralized prompt templates for the HIP agent."""
    
    SYSTEM_ROLE = _TemplateDescriptor("system_role")
    CONTEXT_HEADER = _TemplateDescriptor("context_header")
    CONTEXT_FOOTER = _TemplateDescriptor("context_footer")
    FEW_SHOT_INTRO = _TemplateDescriptor("few_shot_intro")
    INSTRUCTIONS = _TemplateDescriptor("instructions")
    RESPONSE_FORMAT = _TemplateDescriptor("response_format")
    BASIC_INSTRUCTION = _TemplateDescriptor("basic_instruction")


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

