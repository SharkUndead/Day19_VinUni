from __future__ import annotations

from graphrag_lab.graph import KnowledgeGraph
from graphrag_lab.schema import Triple


def answer_with_graph(question: str, graph: KnowledgeGraph) -> str:
    seeds = graph.find_nodes(question)
    if not seeds:
        return "I do not know because no seed node was found in the graph."

    triples = graph.neighborhood(seeds[:3], hops=2)
    if not triples:
        return "I found seed nodes but no related graph facts."

    return synthesize_answer(question, triples)


def synthesize_answer(question: str, triples: list[Triple]) -> str:
    question_lower = question.lower()

    if "when" in question_lower and ("founded" in question_lower or "founded?" in question_lower):
        years = [t for t in triples if t.predicate == "FOUNDED_IN"]
        if years:
            return "; ".join(f"{t.subject} was founded in {t.object}" for t in years[:8]) + "."

    if "co-founded by former google employees" in question_lower:
        companies = sorted(
            {
                founded.subject
                for former in triples
                for founded in triples
                if former.predicate == "FORMERLY_WORKED_AT"
                and former.object == "Google"
                and founded.predicate in {"FOUNDED_BY", "CO_FOUNDED"}
                and founded.object == former.subject
            }
        )
        if companies:
            return "AI companies co-founded by former Google employees include " + ", ".join(companies) + "."

    if "founded" in question_lower or "founder" in question_lower:
        founders = [t for t in triples if t.predicate in {"FOUNDED_BY", "CO_FOUNDED"}]
        if founders:
            return "; ".join(f"{t.subject} was founded or co-founded by {t.object}" for t in founders[:8]) + "."

    if "invested" in question_lower or "investor" in question_lower:
        investments = [t for t in triples if t.predicate == "INVESTED_IN"]
        if investments:
            return "; ".join(f"{t.subject} invested in {t.object}" for t in investments[:8]) + "."

    if "partnered" in question_lower or "partner" in question_lower:
        partnerships = [t for t in triples if t.predicate == "PARTNERED_WITH"]
        if partnerships:
            return "; ".join(f"{t.subject} partnered with {t.object}" for t in partnerships[:8]) + "."

    if "supplies" in question_lower or "accelerators" in question_lower:
        supplies = [t for t in triples if t.predicate == "SUPPLIES_TO"]
        if supplies:
            return "; ".join(f"{t.subject} supplies AI accelerators to {t.object}" for t in supplies[:8]) + "."

    if "develop" in question_lower or "model" in question_lower or "product" in question_lower:
        products = [t for t in triples if t.predicate == "DEVELOPS"]
        if products:
            return "; ".join(f"{t.subject} develops {t.object}" for t in products[:8]) + "."

    if "based" in question_lower or "where" in question_lower:
        locations = [t for t in triples if t.predicate == "BASED_IN"]
        if locations:
            return "; ".join(f"{t.subject} is based in {t.object}" for t in locations[:8]) + "."

    if "acquired" in question_lower:
        acquisitions = [t for t in triples if t.predicate == "ACQUIRED"]
        if acquisitions:
            return "; ".join(f"{t.subject} acquired {t.object}" for t in acquisitions[:8]) + "."

    facts = [f"{t.subject} --{t.predicate}--> {t.object}" for t in triples[:8]]
    return "Relevant graph facts: " + "; ".join(facts) + "."
