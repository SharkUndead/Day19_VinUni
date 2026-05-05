# GraphRAG Benchmark Report

## 1. Pipeline

- Corpus: offline Tech Company Corpus sample in `data/raw/tech_company_corpus.txt` with 12 company summaries, enough for the 10-document lab scope
- Entity/relation extraction: deterministic rule-based extraction for reproducible lab demo
- Optional LLM-based NER: `scripts/extract_triples_llm.py --provider openai` or `--provider groq`
- Graph backend: local directed knowledge graph exported as GraphML
- Node embeddings: local hashed vectors from each node neighborhood
- Flat RAG backend: lexical top-k retrieval baseline
- GraphRAG retrieval strategy: seed-node matching + 2-hop BFS + graph fact synthesis

## 2. Knowledge Graph

- Nodes: 84
- Edges/triples: 105
- Graph export: `data/processed/knowledge_graph.graphml`
- Text visualization: `reports/figures/knowledge_graph_edges.txt`
- Node embeddings: `data\embeddings\node_embeddings.json`
- Node similarity table: `data\embeddings\node_similarity.csv`
- Visualization image: `reports\figures\knowledge_graph.svg`

## 3. Benchmark Summary

| Metric | Flat RAG | GraphRAG |
| --- | ---: | ---: |
| Accuracy | 70.00% | 100.00% |
| Average latency | 0.0 ms | 0.0 ms |
| Estimated query cost | $0.002436 | $0.003825 |

GraphRAG accuracy improvement: 30.00%.

## 4. Hypothetical API Cost Estimate

These costs are estimates only. The offline demo did not call an API. The estimate assumes `gpt-4.1-mini` pricing at $0.40/1M input tokens and $1.60/1M output tokens, with token count approximated as 1 token per 4 characters.

Pricing source checked on 2026-05-05: OpenAI official model pricing for `gpt-4.1-mini` lists text input at $0.40/1M tokens and output at $1.60/1M tokens.

| Item | Input tokens | Output tokens | Estimated cost |
| --- | ---: | ---: | ---: |
| Triple extraction/indexing | 760 | 843 | $0.001653 |
| 20 Flat RAG answer calls | n/a | n/a | $0.002436 |
| 20 GraphRAG answer calls | n/a | n/a | $0.003825 |
| Total GraphRAG pipeline estimate | n/a | n/a | $0.005478 |

In a real API run, token usage should be taken from the API response `usage` field instead of this character-based approximation.

## 5. Failure Modes

- Flat RAG can miss multi-hop links because it retrieves text snippets independently.
- GraphRAG can fail when seed-node matching does not find the right entity or when extracted triples are incomplete.
- The current offline extractor is deterministic and useful for demonstration. An LLM extractor can be used later for a richer 10-article corpus.

## 6. Conclusion

This repository now contains an end-to-end offline GraphRAG lab pipeline. For the final assignment, keep around 10 real company articles or summaries, rerun extraction and benchmark, then add Neo4j screenshots to `reports/figures/`.
