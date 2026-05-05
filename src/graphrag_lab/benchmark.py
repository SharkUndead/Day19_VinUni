from __future__ import annotations

import time

from graphrag_lab.costing import estimate_call_cost
from graphrag_lab.flat_rag import FlatRag
from graphrag_lab.graphrag import answer_with_graph
from graphrag_lab.graph import KnowledgeGraph
from graphrag_lab.schema import BenchmarkResult


def is_correct(answer: str, expected: str) -> bool:
    if not expected or expected.lower().startswith("fill after"):
        return False
    answer_lower = answer.lower()
    expected_terms = [term.strip().lower() for term in expected.split(";") if term.strip()]
    return all(term in answer_lower for term in expected_terms)


def run_benchmark(
    questions: list[dict[str, str]],
    flat_rag: FlatRag,
    graph: KnowledgeGraph,
) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    for row in questions:
        question = row["question"]
        expected = row["expected_answer"]

        start = time.perf_counter()
        flat_answer = flat_rag.answer(question)
        flat_latency = (time.perf_counter() - start) * 1000
        flat_docs = flat_rag.retrieve(question)
        flat_context = "\n".join(doc["text"] for doc in flat_docs)
        _, _, flat_cost = estimate_call_cost(
            f"Question: {question}\nRetrieved context:\n{flat_context}",
            flat_answer,
        )

        start = time.perf_counter()
        graph_answer = answer_with_graph(question, graph)
        graph_latency = (time.perf_counter() - start) * 1000
        seeds = graph.find_nodes(question)
        graph_context = graph.textualize(graph.neighborhood(seeds[:3], hops=2))
        _, _, graph_cost = estimate_call_cost(
            f"Question: {question}\nGraph context:\n{graph_context}",
            graph_answer,
        )

        results.append(
            BenchmarkResult(
                question=question,
                expected_answer=expected,
                flat_rag_answer=flat_answer,
                graphrag_answer=graph_answer,
                flat_rag_correct=is_correct(flat_answer, expected),
                graphrag_correct=is_correct(graph_answer, expected),
                flat_rag_latency_ms=flat_latency,
                graphrag_latency_ms=graph_latency,
                flat_rag_cost_usd=flat_cost,
                graphrag_cost_usd=graph_cost,
                notes="offline run with hypothetical API cost estimate",
            )
        )
    return results


def summarize(results: list[BenchmarkResult]) -> dict[str, float]:
    total = max(len(results), 1)
    return {
        "flat_accuracy": sum(result.flat_rag_correct for result in results) / total,
        "graph_accuracy": sum(result.graphrag_correct for result in results) / total,
        "flat_avg_latency_ms": sum(result.flat_rag_latency_ms for result in results) / total,
        "graph_avg_latency_ms": sum(result.graphrag_latency_ms for result in results) / total,
        "flat_cost_usd": sum(result.flat_rag_cost_usd for result in results),
        "graph_cost_usd": sum(result.graphrag_cost_usd for result in results),
    }
