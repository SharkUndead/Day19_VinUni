from build_graph import main as build_graph
from build_node_embeddings import main as build_node_embeddings
from extract_triples import main as extract_triples
from generate_report import main as generate_report
from generate_visualization import main as generate_visualization
from run_benchmark import main as run_benchmark


def main() -> None:
    extract_triples()
    build_graph()
    build_node_embeddings()
    generate_visualization()
    run_benchmark()
    generate_report()


if __name__ == "__main__":
    main()
