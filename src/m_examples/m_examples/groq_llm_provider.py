"""Generic Groq chat completion provider."""

from __future__ import annotations

import os


class Groq_LLMProvider:
    """Groq chat completion API client."""

    def __init__(self, *, model: str = "llama-3.1-8b-instant", temperature: float = 0.7) -> None:
        """Initialize Groq LLM provider.

        Args:
            model: Groq model identifier
            temperature: Sampling temperature (0.0-1.0)

        Raises:
            RuntimeError: If GROQ_API_KEY not set or groq not installed
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable not set. "
                "Please set it to your Groq API key."
            )

        try:
            from groq import Groq
        except ImportError:
            raise RuntimeError(
                "groq package not installed. "
                "Install with: pip install groq"
            )

        self._client = Groq(api_key=api_key)
        self._model = model
        self._temperature = temperature

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 500,
        reasoning_effort: str = "medium",
    ) -> str:
        """Call Groq chat completion API.

        Args:
            system_prompt: System message defining LLM behavior
            user_message: User query or context
            max_tokens: Maximum tokens in response

        Returns:
            Completion text from LLM
        """
        # Build request parameters
        request_params = {
            "model": self._model,
            "temperature": self._temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": max_tokens,
        }
        
        # Add reasoning_effort for reasoning models
        if "reasoning" in self._model or "gpt-oss" in self._model:
            request_params["reasoning_effort"] = reasoning_effort
            
        response = self._client.chat.completions.create(**request_params)
        return response.choices[0].message.content.strip()


def main():
    """Main entry point for testing Groq LLM provider."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: groq_llm_provider <system_prompt> <user_message>")
        sys.exit(1)
    
    system_prompt = sys.argv[1]
    user_message = sys.argv[2]
    
    try:
        provider = Groq_LLMProvider()
        response = provider.complete(system_prompt, user_message)
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
