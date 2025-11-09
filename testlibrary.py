from token_check import TokenCounter, Provider

# No API key required for OpenAI
counter = TokenCounter()

text = "Hello, world! How many tokens is this message?"

# Count tokens only
result = counter.count_tokens(text, Provider.OPENAI, "gpt-4o")
print(f"OpenAI: {result.tokens} tokens")

# Count tokens with cost estimation
result = counter.count_tokens(text, Provider.OPENAI, "gpt-4o", estimate_cost=True)
print(f"OpenAI: {result.tokens} tokens")
print(f"Estimated cost: ${result.estimated_cost:.6f}")
