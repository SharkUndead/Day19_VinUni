from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from graphrag_lab.schema import BenchmarkResult, Triple


def read_corpus(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    docs: list[dict[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("TITLE:"):
            if current_title and current_lines:
                docs.append({"title": current_title, "text": " ".join(current_lines)})
            current_title = line.removeprefix("TITLE:").strip()
            current_lines = []
        elif line:
            current_lines.append(line)

    if current_title and current_lines:
        docs.append({"title": current_title, "text": " ".join(current_lines)})

    return docs


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_triples_csv(path: Path) -> list[Triple]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return [
            Triple(row["subject"], row["predicate"], row["object"], row.get("source", ""))
            for row in csv.DictReader(file)
        ]


def write_triples_csv(path: Path, triples: Iterable[Triple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["subject", "predicate", "object", "source"])
        writer.writeheader()
        for triple in triples:
            writer.writerow(
                {
                    "subject": triple.subject,
                    "predicate": triple.predicate,
                    "object": triple.object,
                    "source": triple.source,
                }
            )


def write_benchmark_results(path: Path, results: Iterable[BenchmarkResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "question",
        "expected_answer",
        "flat_rag_answer",
        "graphrag_answer",
        "flat_rag_correct",
        "graphrag_correct",
        "flat_rag_latency_ms",
        "graphrag_latency_ms",
        "flat_rag_cost_usd",
        "graphrag_cost_usd",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_row())
