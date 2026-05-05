from __future__ import annotations


MODEL_NAME = "gpt-4.1-mini"
INPUT_USD_PER_1M_TOKENS = 0.40
OUTPUT_USD_PER_1M_TOKENS = 1.60


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def estimate_api_cost(input_tokens: int, output_tokens: int) -> float:
    input_cost = input_tokens / 1_000_000 * INPUT_USD_PER_1M_TOKENS
    output_cost = output_tokens / 1_000_000 * OUTPUT_USD_PER_1M_TOKENS
    return input_cost + output_cost


def estimate_call_cost(input_text: str, output_text: str) -> tuple[int, int, float]:
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    return input_tokens, output_tokens, estimate_api_cost(input_tokens, output_tokens)
