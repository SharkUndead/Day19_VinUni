from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from graphrag_lab.config import settings


class LlmError(RuntimeError):
    pass


def provider_config(provider: str | None = None) -> tuple[str, str, str]:
    selected = (provider or settings.llm_provider).lower()
    if selected == "openai":
        if not settings.openai_api_key:
            raise LlmError("OPENAI_API_KEY is missing in .env")
        return (
            "https://api.openai.com/v1/chat/completions",
            settings.openai_api_key,
            settings.openai_model,
        )
    if selected == "groq":
        if not settings.groq_api_key:
            raise LlmError("GROQ_API_KEY is missing in .env")
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            settings.groq_api_key,
            settings.groq_model,
        )
    raise LlmError(f"Unsupported LLM_PROVIDER: {selected}")


def chat_json(
    system_prompt: str,
    user_prompt: str,
    provider: str | None = None,
    retries: int = 2,
) -> dict[str, object]:
    url, api_key, model = provider_config(provider)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    body = None
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise LlmError(f"LLM API request failed: {error.code} {details}") from error
        except (TimeoutError, urllib.error.URLError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(2**attempt)
                continue
            raise LlmError(f"LLM API request failed after retries: {error}") from error

    if body is None:
        raise LlmError(f"LLM API request failed: {last_error}")

    content = body["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise LlmError(f"LLM returned non-JSON content: {content}") from error
