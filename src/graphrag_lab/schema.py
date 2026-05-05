from dataclasses import dataclass


@dataclass(frozen=True)
class Triple:
    subject: str
    predicate: str
    object: str
    source: str = ""


@dataclass(frozen=True)
class BenchmarkResult:
    question: str
    expected_answer: str
    flat_rag_answer: str
    graphrag_answer: str
    flat_rag_correct: bool
    graphrag_correct: bool
    flat_rag_latency_ms: float
    graphrag_latency_ms: float
    flat_rag_cost_usd: float = 0.0
    graphrag_cost_usd: float = 0.0
    notes: str = ""

    def to_row(self) -> dict[str, object]:
        return {
            "question": self.question,
            "expected_answer": self.expected_answer,
            "flat_rag_answer": self.flat_rag_answer,
            "graphrag_answer": self.graphrag_answer,
            "flat_rag_correct": self.flat_rag_correct,
            "graphrag_correct": self.graphrag_correct,
            "flat_rag_latency_ms": self.flat_rag_latency_ms,
            "graphrag_latency_ms": self.graphrag_latency_ms,
            "flat_rag_cost_usd": self.flat_rag_cost_usd,
            "graphrag_cost_usd": self.graphrag_cost_usd,
            "notes": self.notes,
        }
