from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.extraction import extract_triples
from graphrag_lab.io import read_corpus, write_jsonl, write_triples_csv


CORPUS_PATH = ROOT / "data" / "raw" / "tech_company_corpus.txt"
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"


def main() -> None:
    docs = read_corpus(CORPUS_PATH)
    write_jsonl(CHUNKS_PATH, docs)
    triples = extract_triples(docs)
    write_triples_csv(TRIPLES_PATH, triples)
    print(f"Wrote {len(docs)} chunks to {CHUNKS_PATH}")
    print(f"Wrote {len(triples)} triples to {TRIPLES_PATH}")


if __name__ == "__main__":
    main()
