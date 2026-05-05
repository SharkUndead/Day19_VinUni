from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.config import settings


def mask(value: str | None, prefix: int = 7) -> str:
    if not value:
        return "missing"
    if len(value) <= prefix:
        return "*" * len(value)
    return value[:prefix] + "*" * (len(value) - prefix)


def main() -> None:
    print(f"LLM_PROVIDER={settings.llm_provider}")
    print(f"OPENAI_MODEL={settings.openai_model}")
    print(f"OPENAI_API_KEY={mask(settings.openai_api_key)} len={len(settings.openai_api_key or '')}")
    print(f"GROQ_MODEL={settings.groq_model}")
    print(f"GROQ_API_KEY={mask(settings.groq_api_key, prefix=6)} len={len(settings.groq_api_key or '')}")


if __name__ == "__main__":
    main()
