"""
Token Counter Utility for Multiple LLM Providers

Supports token counting for:
- OpenAI models (via tiktoken) - OFFLINE, no API key needed
- Anthropic Claude models (via Anthropic SDK) - requires API key
- Google Gemini models (via Google GenAI SDK) - requires API key
"""

from enum import Enum
from typing import Any, Dict, NamedTuple

# Constants
DEFAULT_GEMINI_LOCATION = "us-central1"
DEFAULT_TIKTOKEN_ENCODING = "o200k_base"  # Used for newer models like GPT-4o

# Provider mapping for genai-prices library
PROVIDER_MAPPING = {
    "openai": "openai",
    "anthropic": "anthropic",
    "gemini": "google",
}


class Provider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class TokenCountResult(NamedTuple):
    """
    Result of token counting with optional cost estimation.
    
    Attributes:
        tokens: Number of tokens counted.
        estimated_cost: Estimated cost in USD (None if not calculated).
        matched_model: Model ID matched for pricing (None if not matched).
    """
    tokens: int
    estimated_cost: float | None = None
    matched_model: str | None = None


class TokenCounter:
    """
    Unified token counter for multiple LLM providers.
    
    Supports token counting for OpenAI (offline), Anthropic Claude, and Google Gemini.
    Provides optional cost estimation using the genai-prices library.
    """

    def __init__(
        self,
        anthropic_api_key: str | None = None,
        gemini_api_key: str | None = None,
        gemini_project_id: str | None = None,
        gemini_location: str | None = None,
        use_vertex_ai: bool = False,
    ) -> None:
        """
        Initialize the token counter.

        Args:
            anthropic_api_key: API key for Anthropic (required for Claude token counting).
            gemini_api_key: API key for Gemini (required for Gemini token counting).
            gemini_project_id: GCP project ID for Vertex AI.
            gemini_location: GCP location for Vertex AI (defaults to 'us-central1').
            use_vertex_ai: Whether to use Vertex AI for Gemini (default: False).

        Note:
            API keys are only required when counting tokens for providers that require
            API calls (Anthropic and Gemini). OpenAI token counting works offline.
        """
        self.anthropic_api_key = anthropic_api_key
        self.gemini_api_key = gemini_api_key
        self.gemini_project_id = gemini_project_id
        self.gemini_location = gemini_location or DEFAULT_GEMINI_LOCATION
        self.use_vertex_ai = use_vertex_ai

        # Lazy-loaded clients
        self._anthropic_client: Any = None
        self._gemini_client: Any = None
        self._tiktoken_cache: Dict[str, Any] = {}

    def count_tokens(
        self,
        text: str,
        provider: Provider,
        model: str,
        estimate_cost: bool = False,
    ) -> TokenCountResult:
        """
        Count tokens for the given text using the specified provider and model.

        Args:
            text: The text to count tokens for.
            provider: The LLM provider (OpenAI, Anthropic, or Gemini).
            model: The specific model name (e.g., 'gpt-4', 'claude-3-opus-20240229',
                'gemini-2.0-flash-001').
            estimate_cost: Whether to estimate the cost (default: False).

        Returns:
            TokenCountResult with token count and optional cost estimation.

        Raises:
            ValueError: If the provider is not supported, text is empty, or API key
                is missing when required.
            ImportError: If required SDK is not installed.

        Example:
            >>> counter = TokenCounter()
            >>> result = counter.count_tokens("Hello, world!", Provider.OPENAI, "gpt-4o")
            >>> print(result.tokens)
            4

        Note:
            - OpenAI: Always offline, no API key needed.
            - Anthropic: Requires API key (makes API call).
            - Gemini: Requires API key (makes API call).
            - Cost estimation: Only includes input token cost (output tokens unknown).
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        if provider == Provider.OPENAI:
            tokens = self._count_openai_tokens(text, model)
        elif provider == Provider.ANTHROPIC:
            tokens = self._count_anthropic_tokens(text, model)
        elif provider == Provider.GEMINI:
            tokens = self._count_gemini_tokens(text, model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Calculate cost if requested
        if estimate_cost:
            cost, matched_model = self._estimate_cost(tokens, provider, model)
            return TokenCountResult(
                tokens=tokens, estimated_cost=cost, matched_model=matched_model
            )
        return TokenCountResult(tokens=tokens)

    def _count_openai_tokens(self, text: str, model: str) -> int:
        """
        Count tokens using tiktoken for OpenAI models.

        Args:
            text: The text to count tokens for.
            model: The OpenAI model name.

        Returns:
            Number of tokens in the text.

        Raises:
            ImportError: If tiktoken is not installed.
        """
        try:
            import tiktoken
        except ImportError as e:
            raise ImportError(
                "tiktoken is required for OpenAI token counting. "
                "Install it with: pip install tiktoken"
            ) from e

        # Cache encodings for efficiency
        if model not in self._tiktoken_cache:
            try:
                # Try to get encoding for the specific model
                self._tiktoken_cache[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to a default encoding if model not recognized
                self._tiktoken_cache[model] = tiktoken.get_encoding(
                    DEFAULT_TIKTOKEN_ENCODING
                )

        encoding = self._tiktoken_cache[model]
        tokens = encoding.encode(text)
        return len(tokens)

    def _count_anthropic_tokens(self, text: str, model: str) -> int:
        """
        Count tokens using Anthropic SDK.

        Args:
            text: The text to count tokens for.
            model: The Anthropic model name.

        Returns:
            Number of input tokens in the text.

        Raises:
            ImportError: If anthropic SDK is not installed.
            ValueError: If API key is not provided.
        """
        if not self.anthropic_api_key:
            raise ValueError(
                "Anthropic API key is required for token counting. "
                "Provide anthropic_api_key or set ANTHROPIC_API_KEY environment variable."
            )

        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic SDK is required for Claude token counting. "
                "Install it with: pip install anthropic"
            ) from e

        if self._anthropic_client is None:
            self._anthropic_client = Anthropic(api_key=self.anthropic_api_key)

        # Use the count_tokens API
        result = self._anthropic_client.messages.count_tokens(
            model=model, messages=[{"role": "user", "content": text}]
        )

        return result.input_tokens

    def _count_gemini_tokens(self, text: str, model: str) -> int:
        """
        Count tokens using Google GenAI SDK (requires API key).

        Args:
            text: The text to count tokens for.
            model: The Gemini model name.

        Returns:
            Total number of tokens in the text.

        Raises:
            ImportError: If google-genai SDK is not installed.
            ValueError: If API key or project ID is missing when required.
        """
        try:
            from google import genai
        except ImportError as e:
            raise ImportError(
                "google-genai SDK is required for Gemini token counting. "
                "Install it with: pip install google-genai"
            ) from e

        # Initialize client if needed
        if self._gemini_client is None:
            if self.use_vertex_ai:
                if not self.gemini_project_id:
                    raise ValueError(
                        "gemini_project_id is required when use_vertex_ai=True"
                    )
                self._gemini_client = genai.Client(
                    vertexai=True,
                    project=self.gemini_project_id,
                    location=self.gemini_location,
                )
            else:
                if not self.gemini_api_key:
                    raise ValueError(
                        "Gemini API key is required for token counting. "
                        "Provide gemini_api_key or set GEMINI_API_KEY environment variable."
                    )
                self._gemini_client = genai.Client(api_key=self.gemini_api_key)

        # Use the count_tokens API
        response = self._gemini_client.models.count_tokens(model=model, contents=text)

        return response.total_tokens

    def _estimate_cost(
        self, tokens: int, provider: Provider, model: str
    ) -> tuple[float | None, str | None]:
        """
        Estimate the cost for input tokens using genai-prices.

        Args:
            tokens: Number of input tokens.
            provider: The LLM provider.
            model: The model name.

        Returns:
            Tuple of (estimated_cost, matched_model_id).
            Returns (None, None) if pricing data is not available or genai-prices
            is not installed.
        """
        try:
            from genai_prices import Usage, calc_price
        except ImportError:
            # genai-prices is optional, return None if not installed
            return None, None

        # Map our Provider enum to genai-prices provider_id
        provider_id = PROVIDER_MAPPING.get(provider.value)
        if not provider_id:
            return None, None

        try:
            price_data = calc_price(
                Usage(input_tokens=tokens, output_tokens=0),
                model_ref=model,
                provider_id=provider_id,
            )
            return price_data.total_price, price_data.model.id
        except Exception:
            # If pricing fails, return None (model not found, etc.)
            return None, None


def main() -> None:
    """
    Example usage of the TokenCounter.

    Demonstrates token counting for OpenAI (offline), Anthropic, and Gemini.
    Shows cost estimation when genai-prices is available.
    """
    import os

    # Example text
    text = "Hello, world! How many tokens is this message?"

    print("Token counts for:", repr(text))
    print()

    # Example 1: OpenAI (no API key needed)
    print("=== OpenAI (Offline - No API key needed) ===")
    counter = TokenCounter()

    try:
        result = counter.count_tokens(
            text, Provider.OPENAI, "gpt-4o", estimate_cost=True
        )
        print(f"OpenAI (gpt-4o): {result.tokens} tokens")
        if result.estimated_cost is not None:
            print(f"  Estimated cost: ${result.estimated_cost:.6f}")
            if result.matched_model and result.matched_model != "gpt-4o":
                print(f"  (matched to: {result.matched_model})")
    except Exception as e:
        print(f"OpenAI error: {e}")

    print()
    print("=== Anthropic & Gemini (API keys required) ===")

    # Example 2: With API keys
    # GOOGLE_API_KEY takes precedence over GEMINI_API_KEY
    counter_with_keys = TokenCounter(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        gemini_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
    )

    # Anthropic
    try:
        result = counter_with_keys.count_tokens(
            text, Provider.ANTHROPIC, "claude-sonnet-4-20250514", estimate_cost=True
        )
        print(f"Anthropic (claude-sonnet-4): {result.tokens} tokens")
        if result.estimated_cost is not None:
            print(f"  Estimated cost: ${result.estimated_cost:.6f}")
            if (
                result.matched_model
                and result.matched_model != "claude-sonnet-4-20250514"
            ):
                print(f"  (matched to: {result.matched_model})")
    except Exception as e:
        print(f"Anthropic error: {e}")

    # Gemini
    try:
        result = counter_with_keys.count_tokens(
            text, Provider.GEMINI, "gemini-2.0-flash-001", estimate_cost=True
        )
        print(f"Gemini (gemini-2.0-flash): {result.tokens} tokens")
        if result.estimated_cost is not None:
            print(f"  Estimated cost: ${result.estimated_cost:.6f}")
            if (
                result.matched_model
                and result.matched_model != "gemini-2.0-flash-001"
            ):
                print(f"  (matched to: {result.matched_model})")
    except Exception as e:
        print(f"Gemini error: {e}")


if __name__ == "__main__":
    main()
