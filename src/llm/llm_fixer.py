import os
import logging
import re
from functools import lru_cache
from transformers import pipeline

# Load fine-tuned local model
local_llm = pipeline(
    "text-generation",
    model="./codet5_finetuned_final",  # Update path if needed
    device="cpu",
    framework="pt"
)

MAX_CODE_CHARS = 1000

def clean_ai_fix(text):
    """Extract and clean code block from LLM output."""
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return f"```python\n{match.group(1).strip()}\n```"
    return f"```python\n{text.strip()}\n```"

def extract_code_context(code: str, line: int, window: int = 10):
    """Get a snippet around the issue line (±10 lines)."""
    lines = code.splitlines()
    start = max(0, line - window)
    end = min(len(lines), line + window)
    snippet = "\n".join(lines[start:end])
    return snippet[:MAX_CODE_CHARS]  # truncate to safe input size

@lru_cache(maxsize=128)
def get_cached_fix(prompt: str):
    return local_llm(
        prompt,
        max_new_tokens=128,
        do_sample=True,
        temperature=0.7,
        return_full_text=False
    )

def get_ai_fix_local(code_snippet, issue_description, issue_line=None, issue_type=None):
    desc = issue_description.lower()
    tag = (issue_type or "").lower()

    # ✅ Rule-based quick fixes
    if "unused_import" in tag or "unused import" in desc:
        return "```python\n# Removed unused import\n```"
    if "unused_variable" in tag or "never used" in desc:
        return "```python\n_ = 0  # replaced unused variable with '_'\n```"
    if "repeated_function" in tag or "repeated function" in desc:
        return "```python\n# Removed duplicate function definition\n```"
    if "unreachable_code" in tag or "unreachable code" in desc:
        return "```python\n# Removed unreachable code (after return/break/continue)\n```"
    if "inefficient_loop" in tag or "inefficient loop" in desc or "nested loop" in desc:
        return "```python\n# Consider optimizing the loop with a list comprehension or flattening\n```"

    # ✅ Truncate or extract context
    if issue_line is not None:
        code_snippet = extract_code_context(code_snippet, issue_line)
    else:
        code_snippet = code_snippet[:MAX_CODE_CHARS]

    # ✅ Construct LLM prompt
    prompt = f"""You are an expert Python developer performing code reviews.

## Task
Fix the following issue in the Python code below. DO NOT explain — just return the corrected code.

## Issue
{issue_description}

## Code to fix:
```python
{code_snippet}
```"""

    try:
        logging.info(f"[LLM] Prompting for: {issue_description}")
        result = get_cached_fix(prompt)
        ai_fix = result[0]["generated_text"].strip()

        print("🧠 Raw LLM output:\n", ai_fix)

        if "```" not in ai_fix:
            logging.warning("⚠️ LLM response incomplete — returning fallback format")
            return f"```python\n# AI-generated (incomplete)\n{ai_fix}\n```"

        return clean_ai_fix(ai_fix)

    except Exception as e:
        logging.error(f"[LLM Error] {e}")
        return f"```python\n# AI Fix not available for: {issue_description}\n# Error: {str(e)}\n```"
