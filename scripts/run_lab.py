from build_graph import main as build_graph
from extract_triples import main as extract_triples
from generate_report import main as generate_report
from run_benchmark import main as run_benchmark


def main() -> None:
    extract_triples()
    build_graph()
    run_benchmark()
    generate_report()


if __name__ == "__main__":
    main()
