"""Generic OpenAI chat completion provider (moved to positivity_pysch_coach)."""

from __future__ import annotations

import os


class OpenAI_LLMProvider:
    """OpenAI chat completion API client."""

    def __init__(self, *, model: str = "gpt-4o-mini", temperature: float = 0.7) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it to your OpenAI API key."
            )

        try:
            import openai
        except ImportError:
            raise RuntimeError(
                "openai package not installed. "
                "Install with: pip install openai"
            )

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._temperature = temperature

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 500,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: openai_llm_provider <system_prompt> <user_message>")
        sys.exit(1)

    system_prompt = sys.argv[1]
    user_message = sys.argv[2]

    try:
        provider = OpenAI_LLMProvider()
        response = provider.complete(system_prompt, user_message)
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
