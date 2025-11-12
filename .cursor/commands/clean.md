# Code Refactoring Guide: Making Code Idiomatic, Pythonic, and Modular

This guide outlines best practices for writing clean, maintainable Python code, using the tone rewriter factory refactoring as a reference example.

## Table of Contents
1. [Modularity](#modularity)
2. [Idiomatic Python](#idiomatic-python)
3. [Documentation](#documentation)
4. [Error Handling](#error-handling)
5. [Code Organization](#code-organization)
6. [Type Safety](#type-safety)

---

## Modularity

### Principle: Single Responsibility
Each function should do one thing and do it well.

**❌ Bad:**
```python
def writer_factory(tone: str):
    def writer(text: str):
        if not text:
            return "Error: Empty input text"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a writer who writes in {tone} tone"},
                {"role": "user", "content": f"rewrite this text {text}"}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    return writer
```

**✅ Good:**
```python
def build_system_prompt(tone: str) -> str:
    """Build a system prompt for the specified tone."""
    return f"You are a writer who writes in {tone} tone"

def build_user_prompt(text: str) -> str:
    """Build a user prompt for text rewriting."""
    return f"rewrite this text {text}"

def rewrite_text(client: OpenAI, tone: str, text: str, ...) -> str:
    """Rewrite text in a specific tone using the OpenAI API."""
    # Uses the above helper functions
    pass
```

### Benefits of Modularity
- **Testability**: Each function can be tested independently
- **Reusability**: Helper functions can be reused across the codebase
- **Maintainability**: Changes to one concern don't affect others
- **Readability**: Clear function names communicate intent

### Key Practices
1. **Extract constants**: Move magic strings/numbers to module-level constants
2. **Separate concerns**: Split prompt building, API calls, and business logic
3. **Dependency injection**: Pass dependencies as parameters rather than using globals
4. **Small functions**: Aim for functions that fit on one screen

---

## Idiomatic Python

### 1. Type Hints
Always use type hints for function signatures and return types.

**❌ Bad:**
```python
def writer_factory(tone):
    def writer(text):
        # ...
```

**✅ Good:**
```python
def tone_rewriter(tone: str, client: OpenAI | None = None) -> Callable[[str], str]:
    def writer(text: str) -> str:
        # ...
```

### 2. Constants Over Magic Values
Extract configuration values to named constants.

**❌ Bad:**
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Magic string
    temperature=0.5        # Magic number
)
```

**✅ Good:**
```python
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.5

response = client.chat.completions.create(
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE
)
```

### 3. Proper Exception Handling
Raise exceptions instead of returning error strings.

**❌ Bad:**
```python
def writer(text: str):
    if not text:
        return "Error: Empty input text"
```

**✅ Good:**
```python
def rewrite_text(client: OpenAI, tone: str, text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
```

### 4. Use `if __name__ == "__main__"` Guard
Protect example/demo code from running on import.

**❌ Bad:**
```python
formal_writer = writer_factory("formal")
print(formal_writer("Hello"))
```

**✅ Good:**
```python
def main() -> None:
    """Example usage of the tone rewriter factory."""
    formal_writer = tone_rewriter("formal")
    print(formal_writer("Hello"))

if __name__ == "__main__":
    main()
```

### 5. Naming Conventions
- **Functions**: `snake_case` (e.g., `tone_rewriter`, `build_system_prompt`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_MODEL`)
- **Private variables**: Prefix with `_` (e.g., `_client`)
- **Classes**: `PascalCase` (e.g., `ChatCompletion`)

### 6. Use Modern Python Features
- **Union types**: `OpenAI | None` instead of `Optional[OpenAI]` (Python 3.10+)
- **Type annotations**: Use `Callable[[str], str]` for function types
- **F-strings**: Prefer f-strings over `.format()` or `%` formatting

---

## Documentation

### 1. Module-Level Docstrings
Start files with a brief description.

```python
"""Tone Rewriter Factory - Modular implementation with proper documentation."""
```

### 2. Function Docstrings (Google Style)
Use Google-style docstrings with Args, Returns, Raises, and Examples.

**✅ Good:**
```python
def tone_rewriter(tone: str, client: OpenAI | None = None) -> Callable[[str], str]:
    """
    Factory function that returns a tone-specific text rewriter function.
    
    This function creates a closure that captures the tone and OpenAI client,
    returning a callable that rewrites text in the specified tone.
    
    Args:
        tone: The desired writing tone (e.g., 'formal', 'friendly', 'supportive').
        client: Optional OpenAI client instance. If None, uses the module-level client.
    
    Returns:
        A function that takes text as input and returns rewritten text in the specified tone.
    
    Example:
        >>> formal_writer = tone_rewriter("formal")
        >>> formal_writer("Hello, how are you?")
        "Greetings, how are you faring today?"
    """
```

### 3. Inline Comments
Use comments to explain *why*, not *what*. Code should be self-documenting.

**❌ Bad:**
```python
# Initialize OpenAI client
client = OpenAI()  # This creates a client
```

**✅ Good:**
```python
# Initialize OpenAI client (uses OPENAI_API_KEY from environment)
_client = OpenAI()
```

### 4. Docstring Sections
- **Args**: Document all parameters with types and descriptions
- **Returns**: Describe the return value and type
- **Raises**: List exceptions that may be raised
- **Example**: Provide usage examples (especially for public APIs)

---

## Error Handling

### 1. Validate Input Early
Check inputs at the beginning of functions.

```python
def rewrite_text(client: OpenAI, tone: str, text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
    # ... rest of function
```

### 2. Validate Outputs
Check API responses before using them.

```python
message: ChatCompletionMessage = response.choices[0].message
if not message.content:
    raise ValueError("Received empty response from API")
return message.content.strip()
```

### 3. Use Specific Exceptions
Raise appropriate exception types.

- `ValueError`: Invalid input values
- `TypeError`: Wrong type passed
- `AttributeError`: Missing attributes
- `RuntimeError`: General runtime errors

---

## Code Organization

### 1. Import Order
Follow PEP 8 import ordering:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
from typing import Callable  # Standard library
from openai import OpenAI     # Third-party
from dotenv import load_dotenv  # Third-party
# Local imports would go here
```

### 2. Constants Before Functions
Define constants at module level, before functions.

```python
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.5

def build_system_prompt(tone: str) -> str:
    # ...
```

### 3. Function Order
Organize functions from general to specific, or by dependency order:
1. Helper/utility functions first
2. Core business logic
3. Factory/high-level functions
4. Main/entry point last

### 4. Dependency Injection
Make functions testable by accepting dependencies as parameters.

**❌ Bad:**
```python
client = OpenAI()  # Global

def writer(text: str):
    response = client.chat.completions.create(...)  # Uses global
```

**✅ Good:**
```python
def rewrite_text(client: OpenAI, tone: str, text: str) -> str:
    response = client.chat.completions.create(...)  # Uses parameter

def tone_rewriter(tone: str, client: OpenAI | None = None) -> Callable[[str], str]:
    if client is None:
        client = _client  # Fallback to module-level
    # ...
```

---

## Type Safety

### 1. Use Type Hints Everywhere
Add type hints to all function parameters and return types.

```python
def build_system_prompt(tone: str) -> str:
    return f"You are a writer who writes in {tone} tone"
```

### 2. Use Typed Collections
Specify types for collections.

```python
from typing import Callable

def tone_rewriter(tone: str) -> Callable[[str], str]:
    # Returns a function that takes str and returns str
    pass
```

### 3. Use Type Aliases for Complex Types
Create aliases for frequently used complex types.

```python
from typing import TypeAlias

WriterFunction: TypeAlias = Callable[[str], str]
```

### 4. Use Type Checking Tools
- `mypy`: Static type checker
- `pyright`: Fast type checker
- IDE type checking: Enable in your editor

---

## Quick Checklist

When refactoring code, ask yourself:

- [ ] **Modularity**
  - [ ] Does each function have a single responsibility?
  - [ ] Are constants extracted to module level?
  - [ ] Can functions be tested independently?
  - [ ] Are dependencies injected rather than global?

- [ ] **Idiomatic Python**
  - [ ] Are type hints used throughout?
  - [ ] Are magic values replaced with named constants?
  - [ ] Are exceptions used instead of error strings?
  - [ ] Is example code protected with `if __name__ == "__main__"`?

- [ ] **Documentation**
  - [ ] Is there a module-level docstring?
  - [ ] Do all public functions have docstrings?
  - [ ] Are Args, Returns, and Raises documented?
  - [ ] Are examples provided for complex functions?

- [ ] **Error Handling**
  - [ ] Are inputs validated early?
  - [ ] Are outputs validated before use?
  - [ ] Are specific exception types used?

- [ ] **Code Organization**
  - [ ] Are imports properly ordered?
  - [ ] Are functions logically ordered?
  - [ ] Is the code easy to navigate?

---

## Example: Before and After

### Before (Original)
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def writer_factory(tone: str):
    def writer(text:str):
        if not text:
            return "Error: Empty input text"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a writer who writes in {tone} tone"},
                {"role": "user", "content": f"rewrite this text {text}"}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    return writer

formal_writer = writer_factory("formal")
print(formal_writer("Hello, how are you?"))
```

### After (Refactored)
```python
"""Tone Rewriter Factory - Modular implementation with proper documentation."""

from typing import Callable
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from dotenv import load_dotenv

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.5

load_dotenv()
_client = OpenAI()

def build_system_prompt(tone: str) -> str:
    """Build a system prompt for the specified tone."""
    return f"You are a writer who writes in {tone} tone"

def build_user_prompt(text: str) -> str:
    """Build a user prompt for text rewriting."""
    return f"rewrite this text {text}"

def rewrite_text(
    client: OpenAI,
    tone: str,
    text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """Rewrite text in a specific tone using the OpenAI Chat Completions API."""
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
    
    system_prompt = build_system_prompt(tone)
    user_prompt = build_user_prompt(text)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    
    message: ChatCompletionMessage = response.choices[0].message
    if not message.content:
        raise ValueError("Received empty response from API")
    
    return message.content.strip()

def tone_rewriter(tone: str, client: OpenAI | None = None) -> Callable[[str], str]:
    """Factory function that returns a tone-specific text rewriter function."""
    if client is None:
        client = _client
    
    def writer(text: str) -> str:
        return rewrite_text(client, tone, text)
    
    return writer

def main() -> None:
    """Example usage of the tone rewriter factory."""
    formal_writer = tone_rewriter("formal")
    print(formal_writer("Hello, how are you?"))

if __name__ == "__main__":
    main()
```

---

## Additional Resources

- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [The Hitchhiker's Guide to Python](https://docs.python-guide.org/)

---

## Summary

Writing idiomatic, Pythonic, and modular code involves:

1. **Breaking code into small, focused functions** (modularity)
2. **Using type hints and modern Python features** (idiomatic)
3. **Documenting everything clearly** (documentation)
4. **Handling errors properly** (error handling)
5. **Organizing code logically** (organization)

Following these principles makes code more maintainable, testable, and easier for others to understand and contribute to.

