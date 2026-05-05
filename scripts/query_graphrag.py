import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.graphrag import answer_with_graph
from graphrag_lab.graph import KnowledgeGraph
from graphrag_lab.io import read_triples_csv


TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Question to answer with GraphRAG")
    args = parser.parse_args()

    graph = KnowledgeGraph(read_triples_csv(TRIPLES_PATH))
    print(answer_with_graph(args.question, graph))


if __name__ == "__main__":
    main()
