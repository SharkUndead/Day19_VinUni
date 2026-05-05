from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.graph import KnowledgeGraph
from graphrag_lab.io import read_triples_csv


TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"
GRAPHML_PATH = ROOT / "data" / "processed" / "knowledge_graph.graphml"
TEXT_PATH = ROOT / "reports" / "figures" / "knowledge_graph_edges.txt"


def main() -> None:
    triples = read_triples_csv(TRIPLES_PATH)
    graph = KnowledgeGraph(triples)

    GRAPHML_PATH.write_text(graph.to_graphml(), encoding="utf-8")
    TEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEXT_PATH.write_text(graph.textualize(triples), encoding="utf-8")

    print(f"Graph nodes: {len(graph.nodes)}")
    print(f"Graph edges: {len(graph.triples)}")
    print(f"Wrote GraphML to {GRAPHML_PATH}")
    print(f"Wrote text visualization to {TEXT_PATH}")


if __name__ == "__main__":
    main()
