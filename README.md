# Token Check

> A simple Python tool to count tokens and estimate costs for OpenAI, Anthropic Claude, and Google Gemini models.

**Token Check** helps you understand how many tokens your text will use before sending it to an LLM, and optionally estimates the cost. Perfect for budgeting, debugging, and optimizing your prompts.

## Table of Contents

- [Quick Start](#quick-start)
- [What Are Tokens?](#what-are-tokens)
- [Features](#features)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Python API](#python-api)
- [Supported Models](#supported-models)
- [API Keys Setup](#api-keys-setup)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Quick Start

**Try it right now** (no API key needed for OpenAI):

```bash
# Install dependencies
uv sync

# Count tokens for OpenAI (works offline!)
uv run token-check openai "Hello, world!"
# Output: Openai (gpt-4o) (offline): 4 tokens

# Estimate cost too
uv run token-check openai "Hello, world!" --cost
# Output:
# Openai (gpt-4o) (offline): 4 tokens
# Estimated cost: $0.000010 (input tokens only)
```

That's it! 🎉

## What Are Tokens?

Tokens are the basic units that LLMs use to process text. Think of them as "words" but more flexible:
- **1 token** ≈ **4 characters** (roughly)
- **1 token** ≈ **0.75 words** (roughly)
- For example: "Hello, world!" = **4 tokens**

**Why does this matter?**
- LLMs charge per token (input + output)
- Knowing token count helps you:
  - Estimate costs before making API calls
  - Debug why prompts are too long
  - Optimize your text to fit within limits

## Features

### ✅ Token Counting

- **OpenAI**: Works **offline** using `tiktoken` - no API key needed!
- **Anthropic Claude**: Uses official API (requires API key)
- **Google Gemini**: Uses official API (requires API key)

### 💰 Cost Estimation

- Estimates costs using the [`genai-prices`](https://github.com/pydantic/genai-prices) library
- Works with all three providers
- Automatically matches model names to pricing data
- ⚠️ **Note**: Only estimates input token costs (output tokens are unknown until the model responds)

### 🚀 Easy to Use

- Simple command-line interface
- Python API for integration
- Works with files, stdin, or direct text input

## Installation

### Option 1: Using `uv` (Recommended)

```bash
# Clone or navigate to the project
cd token-check

# Install dependencies (creates virtual environment automatically)
uv sync

# Start using it!
uv run token-check openai "Hello!"
```

### Option 2: Using `pip`

```bash
# Generate requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Install dependencies
pip install -r requirements.txt

# Or install directly
pip install tiktoken anthropic google-genai genai-prices
```

## Usage Examples

### Basic Token Counting

```bash
# Count tokens for OpenAI (no API key needed)
uv run token-check openai "Hello, world!"
# Output: Openai (gpt-4o) (offline): 4 tokens

# Count tokens for Anthropic (requires API key)
export ANTHROPIC_API_KEY="your-key"
uv run token-check anthropic "Hello, world!"
# Output: Anthropic (claude-sonnet-4-20250514): 12 tokens

# Count tokens for Gemini (requires API key)
export GOOGLE_API_KEY="your-key"
uv run token-check gemini "Hello, world!"
# Output: Gemini (gemini-2.5-flash): 4 tokens
```

### Reading from Files

```bash
# Count tokens in a file
uv run token-check openai --file document.txt

# Or use stdin
cat document.txt | uv run token-check openai -
echo "Hello!" | uv run token-check gemini -
```

### Specifying Models

```bash
# Use a specific model
uv run token-check openai "Hello!" --model gpt-4-turbo
uv run token-check gemini "Hello!" --model gemini-1.5-pro
```

### Cost Estimation

```bash
# Get token count + cost estimate
uv run token-check openai "Hello, world!" --cost
# Output:
# Openai (gpt-4o) (offline): 4 tokens
# Estimated cost: $0.000010 (input tokens only)

# Quiet mode (just numbers: tokens,cost)
uv run token-check openai "Hello!" --cost --quiet
# Output: 4,0.000010
```

### Getting Help

```bash
# See all available options
uv run token-check --help
```

## Python API

### Basic Usage (OpenAI - No API Key)

```python
from token_check import TokenCounter, Provider

# Create a counter (no API key needed for OpenAI)
counter = TokenCounter()

# Count tokens
text = "Hello, world! How many tokens is this?"
result = counter.count_tokens(text, Provider.OPENAI, "gpt-4o")
print(f"Tokens: {result.tokens}")

# With cost estimation
result = counter.count_tokens(
    text, Provider.OPENAI, "gpt-4o", estimate_cost=True
)
print(f"Tokens: {result.tokens}")
print(f"Cost: ${result.estimated_cost:.6f}")
```

### Using with API Keys (Anthropic & Gemini)

```python
from token_check import TokenCounter, Provider
import os

# Initialize with API keys
counter = TokenCounter(
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    gemini_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
)

text = "Hello, world!"

# Count tokens for Anthropic
result = counter.count_tokens(
    text, Provider.ANTHROPIC, "claude-sonnet-4-20250514", estimate_cost=True
)
print(f"Anthropic: {result.tokens} tokens")
if result.estimated_cost:
    print(f"Cost: ${result.estimated_cost:.6f}")

# Count tokens for Gemini
result = counter.count_tokens(text, Provider.GEMINI, "gemini-2.0-flash-001")
print(f"Gemini: {result.tokens} tokens")
```

### Running the Example Script

```bash
# OpenAI only (no API keys needed)
python token_check.py

# With API keys for full functionality
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
python token_check.py
```

## Supported Models

### OpenAI Models
- `gpt-4o`, `gpt-4o-mini` (recommended)
- `gpt-4`, `gpt-4-turbo`
- `gpt-3.5-turbo`
- Any model supported by `tiktoken`

### Anthropic Claude Models
- `claude-sonnet-4-20250514` (latest)
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

### Google Gemini Models
- `gemini-2.0-flash-001`
- `gemini-2.5-flash`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

## API Keys Setup

### Quick Reference

| Provider | API Key Required? | How It Works |
|----------|-------------------|--------------|
| **OpenAI** | ❌ No | Uses `tiktoken` - works completely offline |
| **Anthropic** | ✅ Yes | Requires API call to count tokens |
| **Gemini** | ✅ Yes | Requires API call to count tokens |

### Setting Up API Keys

**For Anthropic:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

**For Gemini:**
```bash
# Option 1: Use GOOGLE_API_KEY (recommended)
export GOOGLE_API_KEY="your-google-api-key"

# Option 2: Use GEMINI_API_KEY
export GEMINI_API_KEY="your-gemini-api-key"
```

**Note**: `GOOGLE_API_KEY` takes precedence over `GEMINI_API_KEY` if both are set.

### Getting API Keys

- **Anthropic**: Get your API key from [console.anthropic.com](https://console.anthropic.com)
- **Google**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Advanced Usage

### Using Vertex AI (Gemini)

If you're using Google Cloud Platform's Vertex AI instead of the Gemini API:

```python
from token_check import TokenCounter, Provider

counter = TokenCounter(
    gemini_project_id="your-gcp-project-id",
    gemini_location="us-central1",  # or your preferred region
    use_vertex_ai=True
)

result = counter.count_tokens(
    "Hello, world!", Provider.GEMINI, "gemini-2.0-flash-001"
)
```

### Error Handling

```python
from token_check import TokenCounter, Provider

counter = TokenCounter()

try:
    result = counter.count_tokens("", Provider.OPENAI, "gpt-4o")
except ValueError as e:
    print(f"Invalid input: {e}")
    # Output: Invalid input: Input text cannot be empty

try:
    result = counter.count_tokens(
        "Hello", Provider.ANTHROPIC, "claude-sonnet-4-20250514"
    )
except ValueError as e:
    print(f"Missing API key: {e}")
    # Output: Missing API key: Anthropic API key is required...
```

## Troubleshooting

### Common Issues

**Problem**: `ImportError: tiktoken is required...`
```bash
# Solution: Install tiktoken
pip install tiktoken
# or
uv sync
```

**Problem**: `ValueError: Anthropic API key is required...`
```bash
# Solution: Set your API key
export ANTHROPIC_API_KEY="your-key"
```

**Problem**: `ValueError: Input text cannot be empty`
```bash
# Solution: Make sure you're providing text
uv run token-check openai "Your text here"
```

**Problem**: Cost estimation shows `None`
```bash
# Solution: Install genai-prices (optional dependency)
pip install genai-prices
# or
uv sync
```

### Getting Help

- Check the help: `uv run token-check --help`
- Run the example script: `python token_check.py`
- Check that your API keys are set: `echo $ANTHROPIC_API_KEY`

## License

MIT License - feel free to use this in your projects!

---

**Made with ❤️ for the LLM community**
