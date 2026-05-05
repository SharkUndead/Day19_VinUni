from pathlib import Path
import sys
import csv


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.benchmark import summarize
from graphrag_lab.costing import (
    INPUT_USD_PER_1M_TOKENS,
    MODEL_NAME,
    OUTPUT_USD_PER_1M_TOKENS,
    estimate_call_cost,
)
from graphrag_lab.io import read_corpus, read_triples_csv
from graphrag_lab.schema import BenchmarkResult


RESULTS_PATH = ROOT / "reports" / "benchmarks" / "results.csv"
TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"
CORPUS_PATH = ROOT / "data" / "raw" / "tech_company_corpus.txt"
REPORT_PATH = ROOT / "reports" / "report.md"
EMBEDDINGS_PATH = ROOT / "data" / "embeddings" / "node_embeddings.json"
SIMILARITY_PATH = ROOT / "data" / "embeddings" / "node_similarity.csv"
NETWORKX_PNG_PATH = ROOT / "reports" / "figures" / "knowledge_graph_networkx.png"
SVG_PATH = ROOT / "reports" / "figures" / "knowledge_graph.svg"


def read_results() -> list[BenchmarkResult]:
    with RESULTS_PATH.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return [
        BenchmarkResult(
            question=row["question"],
            expected_answer=row["expected_answer"],
            flat_rag_answer=row["flat_rag_answer"],
            graphrag_answer=row["graphrag_answer"],
            flat_rag_correct=row["flat_rag_correct"].lower() == "true",
            graphrag_correct=row["graphrag_correct"].lower() == "true",
            flat_rag_latency_ms=float(row["flat_rag_latency_ms"]),
            graphrag_latency_ms=float(row["graphrag_latency_ms"]),
            flat_rag_cost_usd=float(row["flat_rag_cost_usd"]),
            graphrag_cost_usd=float(row["graphrag_cost_usd"]),
            notes=row["notes"],
        )
        for row in rows
    ]


def main() -> None:
    triples = read_triples_csv(TRIPLES_PATH)
    results = read_results()
    summary = summarize(results)
    improvement = summary["graph_accuracy"] - summary["flat_accuracy"]
    docs = read_corpus(CORPUS_PATH)
    corpus_text = "\n".join(doc["text"] for doc in docs)
    triples_text = "\n".join(f"{t.subject},{t.predicate},{t.object}" for t in triples)
    indexing_input_tokens, indexing_output_tokens, indexing_cost = estimate_call_cost(
        "Extract knowledge graph triples from this corpus:\n" + corpus_text,
        triples_text,
    )

    REPORT_PATH.write_text(
        f"""# GraphRAG Benchmark Report

## 1. Pipeline

- Corpus: offline Tech Company Corpus sample in `data/raw/tech_company_corpus.txt` with 12 company summaries, enough for the 10-document lab scope
- Entity/relation extraction: deterministic rule-based extraction for reproducible lab demo
- Optional LLM-based NER: `scripts/extract_triples_llm.py --provider openai` or `--provider groq`
- Graph backend: local directed knowledge graph exported as GraphML
- Node embeddings: local hashed vectors from each node neighborhood
- Flat RAG backend: lexical top-k retrieval baseline
- GraphRAG retrieval strategy: seed-node matching + 2-hop BFS + graph fact synthesis

## 2. Knowledge Graph

- Nodes: {len(set(t.subject for t in triples) | set(t.object for t in triples))}
- Edges/triples: {len(triples)}
- Graph export: `data/processed/knowledge_graph.graphml`
- Text visualization: `reports/figures/knowledge_graph_edges.txt`
- Node embeddings: `{EMBEDDINGS_PATH.relative_to(ROOT)}`
- Node similarity table: `{SIMILARITY_PATH.relative_to(ROOT)}`
- Visualization image: `{(NETWORKX_PNG_PATH if NETWORKX_PNG_PATH.exists() else SVG_PATH).relative_to(ROOT)}`

## 3. Benchmark Summary

| Metric | Flat RAG | GraphRAG |
| --- | ---: | ---: |
| Accuracy | {summary['flat_accuracy']:.2%} | {summary['graph_accuracy']:.2%} |
| Average latency | {summary['flat_avg_latency_ms']:.1f} ms | {summary['graph_avg_latency_ms']:.1f} ms |
| Estimated query cost | ${summary['flat_cost_usd']:.6f} | ${summary['graph_cost_usd']:.6f} |

GraphRAG accuracy improvement: {improvement:.2%}.

## 4. Hypothetical API Cost Estimate

These costs are estimates only. The offline demo did not call an API. The estimate assumes `{MODEL_NAME}` pricing at ${INPUT_USD_PER_1M_TOKENS:.2f}/1M input tokens and ${OUTPUT_USD_PER_1M_TOKENS:.2f}/1M output tokens, with token count approximated as 1 token per 4 characters.

Pricing source checked on 2026-05-05: OpenAI official model pricing for `gpt-4.1-mini` lists text input at $0.40/1M tokens and output at $1.60/1M tokens.

| Item | Input tokens | Output tokens | Estimated cost |
| --- | ---: | ---: | ---: |
| Triple extraction/indexing | {indexing_input_tokens} | {indexing_output_tokens} | ${indexing_cost:.6f} |
| 20 Flat RAG answer calls | n/a | n/a | ${summary['flat_cost_usd']:.6f} |
| 20 GraphRAG answer calls | n/a | n/a | ${summary['graph_cost_usd']:.6f} |
| Total GraphRAG pipeline estimate | n/a | n/a | ${(indexing_cost + summary['graph_cost_usd']):.6f} |

In a real API run, token usage should be taken from the API response `usage` field instead of this character-based approximation.

## 5. Failure Modes

- Flat RAG can miss multi-hop links because it retrieves text snippets independently.
- GraphRAG can fail when seed-node matching does not find the right entity or when extracted triples are incomplete.
- The current offline extractor is deterministic and useful for demonstration. An LLM extractor can be used later for a richer 10-article corpus.

## 6. Conclusion

This repository now contains an end-to-end offline GraphRAG lab pipeline. For the final assignment, keep around 10 real company articles or summaries, rerun extraction and benchmark, then add Neo4j screenshots to `reports/figures/`.
""",
        encoding="utf-8",
    )
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
