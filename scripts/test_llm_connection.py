from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.llm import chat_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["openai", "groq"], default="openai")
    args = parser.parse_args()

    response = chat_json(
        "Return JSON only.",
        'Return {"ok": true, "message": "connection works"}.',
        provider=args.provider,
        retries=1,
    )
    print(response)


if __name__ == "__main__":
    main()
