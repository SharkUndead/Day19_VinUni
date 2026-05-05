from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

from graphrag_lab.schema import Triple


VECTOR_SIZE = 64


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def hashed_embedding(text: str, size: int = VECTOR_SIZE) -> list[float]:
    vector = [0.0] * size
    for token in tokenize(text):
        digest = hashlib.md5(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % size
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def node_descriptions(triples: list[Triple]) -> dict[str, str]:
    descriptions: dict[str, list[str]] = defaultdict(list)
    for triple in triples:
        descriptions[triple.subject].append(f"{triple.subject} {triple.predicate} {triple.object}")
        descriptions[triple.object].append(f"{triple.subject} {triple.predicate} {triple.object}")
    return {node: ". ".join(parts) for node, parts in descriptions.items()}


def build_node_embeddings(triples: list[Triple]) -> dict[str, dict[str, object]]:
    descriptions = node_descriptions(triples)
    return {
        node: {
            "description": description,
            "embedding_model": "local-hash-vector-v1",
            "embedding": hashed_embedding(description),
        }
        for node, description in sorted(descriptions.items())
    }


def write_node_embeddings(path: Path, triples: list[Triple]) -> dict[str, dict[str, object]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    embeddings = build_node_embeddings(triples)
    path.write_text(json.dumps(embeddings, indent=2, ensure_ascii=False), encoding="utf-8")
    return embeddings


def write_similarity_csv(path: Path, embeddings: dict[str, dict[str, object]], top_k: int = 5) -> None:
    rows: list[tuple[str, str, float]] = []
    items = [(node, data["embedding"]) for node, data in embeddings.items()]
    for index, (node, vector) in enumerate(items):
        scored: list[tuple[float, str]] = []
        for other, other_vector in items:
            if other == node:
                continue
            scored.append((cosine_similarity(vector, other_vector), other))
        for score, other in sorted(scored, reverse=True)[:top_k]:
            rows.append((node, other, score))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write("node,similar_node,cosine_similarity\n")
        for node, other, score in rows:
            file.write(f'"{node}","{other}",{score:.6f}\n')
