import csv
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.benchmark import run_benchmark, summarize
from graphrag_lab.flat_rag import FlatRag
from graphrag_lab.graph import KnowledgeGraph
from graphrag_lab.io import read_corpus, read_triples_csv, write_benchmark_results


CORPUS_PATH = ROOT / "data" / "raw" / "tech_company_corpus.txt"
QUESTIONS_PATH = ROOT / "reports" / "benchmarks" / "questions.csv"
RESULTS_PATH = ROOT / "reports" / "benchmarks" / "results.csv"
TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"
SUMMARY_PATH = ROOT / "reports" / "benchmarks" / "summary.csv"


def main() -> None:
    with QUESTIONS_PATH.open("r", encoding="utf-8", newline="") as file:
        questions = list(csv.DictReader(file))

    docs = read_corpus(CORPUS_PATH)
    graph = KnowledgeGraph(read_triples_csv(TRIPLES_PATH))
    results = run_benchmark(questions, FlatRag(docs), graph)
    summary = summarize(results)

    write_benchmark_results(RESULTS_PATH, results)
    with SUMMARY_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["metric", "value"])
        for metric, value in summary.items():
            writer.writerow([metric, value])

    print(f"Wrote benchmark results to {RESULTS_PATH}")
    print(f"Wrote benchmark summary to {SUMMARY_PATH}")
    print(f"Flat RAG accuracy: {summary['flat_accuracy']:.2%}")
    print(f"GraphRAG accuracy: {summary['graph_accuracy']:.2%}")


if __name__ == "__main__":
    main()
