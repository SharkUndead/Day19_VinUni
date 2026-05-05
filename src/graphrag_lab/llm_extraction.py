from __future__ import annotations

from graphrag_lab.extraction import deduplicate_triples, normalize_entity
from graphrag_lab.llm import chat_json
from graphrag_lab.schema import Triple


SYSTEM_PROMPT = """You extract knowledge graph triples from technology company text.
Return JSON only with this shape:
{
  "triples": [
    {"subject": "...", "predicate": "FOUNDED_BY", "object": "..."}
  ]
}
Use concise entity names. Use uppercase snake_case predicates.
Prefer relations such as IS_A, FOUNDED_BY, FOUNDED_IN, CEO_OF, DEVELOPES, DEVELOPS, ACQUIRED, INVESTED_IN, PARTNERED_WITH, FORMERLY_WORKED_AT, WORKS_AT, BASED_IN, CO_FOUNDED, SUPPLIES_TO.
Do not invent facts not present in the text."""


def extract_triples_with_llm(docs: list[dict[str, str]], provider: str | None = None) -> list[Triple]:
    triples: list[Triple] = []
    for doc in docs:
        response = chat_json(
            SYSTEM_PROMPT,
            f"Source title: {doc['title']}\nText:\n{doc['text']}",
            provider=provider,
        )
        for item in response.get("triples", []):
            if not isinstance(item, dict):
                continue
            subject = normalize_entity(str(item.get("subject", "")))
            predicate = str(item.get("predicate", "")).strip().upper().replace(" ", "_")
            obj = normalize_entity(str(item.get("object", "")))
            if subject and predicate and obj:
                if predicate == "DEVELOPNES":
                    predicate = "DEVELOPS"
                triples.append(Triple(subject, predicate, obj, doc["title"]))
    return deduplicate_triples(triples)
