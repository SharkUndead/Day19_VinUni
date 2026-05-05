from __future__ import annotations

import re


STOPWORDS = {
    "the",
    "is",
    "a",
    "an",
    "of",
    "by",
    "and",
    "in",
    "to",
    "what",
    "which",
    "who",
    "are",
    "was",
    "were",
    "with",
}


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS}


class FlatRag:
    def __init__(self, docs: list[dict[str, str]]) -> None:
        self.docs = docs
        self.index = [(doc, tokenize(doc["title"] + " " + doc["text"])) for doc in docs]

    def retrieve(self, question: str, top_k: int = 2) -> list[dict[str, str]]:
        query_tokens = tokenize(question)
        scored = [
            (len(query_tokens & tokens), doc)
            for doc, tokens in self.index
            if len(query_tokens & tokens) > 0
        ]
        return [doc for _, doc in sorted(scored, key=lambda item: item[0], reverse=True)[:top_k]]

    def answer(self, question: str) -> str:
        docs = self.retrieve(question)
        if not docs:
            return "I do not know based on the corpus."

        context = " ".join(doc["text"] for doc in docs)
        sentences = [sentence.strip() for sentence in context.split(".") if sentence.strip()]
        query_tokens = tokenize(question)
        scored = [
            (len(query_tokens & tokenize(sentence)), sentence)
            for sentence in sentences
        ]
        best = [sentence for score, sentence in sorted(scored, reverse=True) if score > 0][:3]
        return ". ".join(best) + "." if best else docs[0]["text"].split(".")[0] + "."
