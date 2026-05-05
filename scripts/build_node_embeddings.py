from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.embeddings import write_node_embeddings, write_similarity_csv
from graphrag_lab.io import read_triples_csv


TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"
EMBEDDINGS_PATH = ROOT / "data" / "embeddings" / "node_embeddings.json"
SIMILARITY_PATH = ROOT / "data" / "embeddings" / "node_similarity.csv"


def main() -> None:
    triples = read_triples_csv(TRIPLES_PATH)
    embeddings = write_node_embeddings(EMBEDDINGS_PATH, triples)
    write_similarity_csv(SIMILARITY_PATH, embeddings)
    print(f"Wrote {len(embeddings)} node embeddings to {EMBEDDINGS_PATH}")
    print(f"Wrote node similarity table to {SIMILARITY_PATH}")


if __name__ == "__main__":
    main()
