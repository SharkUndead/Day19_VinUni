from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.io import read_corpus, write_jsonl, write_triples_csv
from graphrag_lab.llm_extraction import extract_triples_with_llm


CORPUS_PATH = ROOT / "data" / "raw" / "tech_company_corpus.txt"
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
TRIPLES_PATH = ROOT / "data" / "processed" / "triples_llm.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["openai", "groq"], default=None)
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N docs")
    args = parser.parse_args()

    docs = read_corpus(CORPUS_PATH)
    if args.limit is not None:
        docs = docs[: args.limit]
    write_jsonl(CHUNKS_PATH, docs)
    triples = extract_triples_with_llm(docs, provider=args.provider)
    write_triples_csv(TRIPLES_PATH, triples)
    print(f"Wrote {len(docs)} chunks to {CHUNKS_PATH}")
    print(f"Wrote {len(triples)} LLM triples to {TRIPLES_PATH}")


if __name__ == "__main__":
    main()
