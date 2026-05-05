import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.flat_rag import FlatRag
from graphrag_lab.io import read_corpus


CORPUS_PATH = ROOT / "data" / "raw" / "tech_company_corpus.txt"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Question to answer with Flat RAG baseline")
    args = parser.parse_args()

    flat_rag = FlatRag(read_corpus(CORPUS_PATH))
    print(flat_rag.answer(args.question))


if __name__ == "__main__":
    main()
