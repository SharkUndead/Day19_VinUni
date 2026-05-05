# Dan y hoan thanh Lab Day 19: GraphRAG voi Tech Company Corpus

## 1. Yeu cau chinh tu 2 file markdown

- Xay dung Knowledge Graph va GraphRAG agent tren Tech Company Corpus.
- Corpus muc tieu: khoang 10 bai/tom tat ve cac cong ty AI.
- Trich xuat entity va relation bang LLM-based NER, output la triples dang `(subject, predicate, object)`.
- Build graph bang NetworkX hoac Neo4j, uu tien Neo4j neu can visualization ro rang.
- Them embeddings cho nodes/chunks de ho tro retrieval.
- GraphRAG retrieval pipeline: query -> seed nodes -> BFS traversal -> subgraph to text -> LLM answer.
- So sanh GraphRAG voi Flat RAG tren 20 cau hoi multi-hop.
- Metrics can bao cao: accuracy, latency, cost/token usage.
- Muc tieu: multi-hop accuracy cua GraphRAG cao hon Flat RAG >= 20%.
- Deliverables: GitHub repository, source code/notebook, visualization Knowledge Graph, benchmark report, failure mode analysis.

## 2. Cau truc thu muc project

```text
.
+-- .venv/                         # Virtual environment local
+-- .env                           # Bien moi truong local, khong commit
+-- .env.example                   # Mau bien moi truong
+-- .gitignore
+-- pyproject.toml
+-- requirements.txt
+-- README.md                      # De bai lab
+-- assigment.md                   # Dan y va checklist
+-- data/
|   +-- raw/                       # Corpus goc: company docs
|   +-- processed/                 # Chunks, triples, graph exports
|   +-- embeddings/                # Embeddings/vector index local
+-- notebooks/                     # Notebook thu nghiem va truc quan hoa
+-- reports/
|   +-- figures/                   # Anh Neo4j/NetworkX graph
|   +-- benchmarks/                # Questions, results, metrics
+-- scripts/                       # Script indexing/query/evaluation
+-- src/
|   +-- graphrag_lab/
|       +-- __init__.py
|       +-- config.py              # Doc .env
|       +-- schema.py              # Triple/BenchmarkResult
+-- tests/
    +-- test_schema.py
```

## 3. Setup moi truong

1. Kich hoat venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Cai dependencies:

```powershell
pip install -r requirements.txt
```

3. Dien `.env`:

```text
OPENAI_API_KEY=...
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
GRAPH_BACKEND=networkx
```

4. Neu dung Neo4j:

- Cai Neo4j Desktop hoac chay Neo4j bang Docker.
- Tao database local.
- Dung Neo4j Browser/Bloom de chup visualization.

5. Kiem tra setup:

```powershell
python -m pytest
```

## 4. Research can tra loi trong bao cao

### Entity Extraction

LLM can phan biet:

- Entity/node: doi tuong co dinh danh rieng, vi du `OpenAI`, `Sam Altman`, `Google`.
- Attribute: thong tin mo ta entity, vi du nam thanh lap, linh vuc, tru so.
- Relation/edge: moi quan he giua 2 entity/value, vi du `FOUNDED_BY`, `WORKED_AT`, `FOUNDED_IN`.

Nen yeu cau LLM output theo schema JSON hoac triples de de validate.

### Deduplication

Deduplication quan trong vi cung mot entity co the xuat hien duoi nhieu ten: `OpenAI`, `OpenAI Inc.`, `Open AI`. Neu khong gop lai, graph bi tach manh, BFS thieu duong lien ket va cau tra loi multi-hop de sai.

### BFS vs vector search

- BFS tren graph tim thong tin bang duong lien ket ro rang theo hop.
- Vector search tim doan van gan nghia, nhung khong dam bao co chuoi quan he logic.
- GraphRAG manh hon Flat RAG o cau hoi can multi-hop, vi du "AI companies co-founded by former Google employees".

## 5. Checklist implementation

### A. Chuan bi corpus

- Dat corpus vao `data/raw/`, vi du `data/raw/tech_company_corpus.txt` hoac nhieu file `.txt/.md`.
- Neu chua co corpus, tao dataset tu khoang 10 bai/tom tat ve cac cong ty AI.
- Chunk corpus va luu `data/processed/chunks.jsonl`.
- Moi chunk nen co: `chunk_id`, `source`, `title`, `text`.

### B. Indexing va trich xuat triples

- Viet `scripts/extract_triples.py`.
- Doc chunks tu `data/processed/chunks.jsonl`.
- Goi LLM de trich triples.
- Validate output theo schema:

```text
subject,predicate,object,source_chunk
```

- Luu ket qua vao `data/processed/triples.csv`.
- Chuan hoa entity va loai triple trung lap.

### C. Build graph

- Viet `scripts/build_graph.py`.
- Ban dau dung NetworkX de chay offline:
  - node = subject/object;
  - edge = predicate;
  - edge attributes = source chunk, confidence neu co.
- Luu graph ra `data/processed/knowledge_graph.graphml`.
- Neu dung Neo4j:
  - import triples bang Cypher;
  - tao constraints cho entity name;
  - chup anh graph/subgraph vao `reports/figures/`.

### D. Them embeddings

- Embed chunks cho Flat RAG.
- Embed node descriptions hoac textualized triples cho GraphRAG.
- Luu vector index vao `data/embeddings/`.
- Neu dung ChromaDB/Faiss, dam bao folder index nam trong `.gitignore`.

### E. GraphRAG retrieval

- Viet `scripts/query_graphrag.py`.
- Pipeline:
  1. Nhan question.
  2. Xac dinh seed nodes bang entity extraction hoac fuzzy match.
  3. BFS traversal trong pham vi 2-hop.
  4. Convert subgraph thanh context text.
  5. Goi LLM de generate answer dua tren context.

### F. Flat RAG baseline

- Viet `scripts/query_flat_rag.py`.
- Chunk corpus.
- Embed chunks.
- Retrieve top-k bang ChromaDB/Faiss.
- Goi LLM de tra loi.
- Luu answer, latency va cost.

### G. Benchmark

- Tao `reports/benchmarks/questions.csv` gom 20 cau hoi multi-hop.
- Chay tung cau hoi tren Flat RAG va GraphRAG.
- Luu `reports/benchmarks/results.csv`.
- Cot can co:
  - `question`
  - `expected_answer`
  - `flat_rag_answer`
  - `graphrag_answer`
  - `flat_rag_correct`
  - `graphrag_correct`
  - `flat_rag_latency_ms`
  - `graphrag_latency_ms`
  - `flat_rag_cost_usd`
  - `graphrag_cost_usd`
  - `notes`

### H. Failure mode analysis

- Tim cac cau Flat RAG hallucinate nhung GraphRAG dung.
- Tim cac cau GraphRAG sai do:
  - thieu entity trong graph;
  - deduplication kem;
  - seed node sai;
  - BFS lay thieu/qua nhieu context;
  - triples sai do LLM extraction.

### I. Bao cao cuoi

- Mo ta pipeline tu raw corpus den benchmark.
- Chen visualization cua Knowledge Graph.
- Chen bang accuracy/latency/cost.
- Chung minh GraphRAG multi-hop accuracy cao hon Flat RAG >= 20% neu dat.
- Neu chua dat, phan tich ly do va de xuat cai thien.

## 6. Thu tu lam nhanh trong 2 gio

1. Cai dependencies va dien `.env`.
2. Chuan bi corpus khoang 10 cong ty AI.
3. Trich triples cho 10-20 documents dau tien.
4. Build graph NetworkX va chup visualization.
5. Viet GraphRAG 2-hop query.
6. Viet Flat RAG baseline don gian.
7. Tao 20 cau hoi benchmark.
8. Chay benchmark, tinh accuracy/latency/cost.
9. Viet report va day len GitHub.

## 7. Trang thai hien tai

- Da tao `.venv` bang Python 3.11.5.
- Da tao `.env`, `.env.example`, `.gitignore`, `requirements.txt`, `pyproject.toml`.
- Da tao cau truc thu muc chinh va package `src/graphrag_lab`.
- Da tao corpus demo tai `data/raw/tech_company_corpus.txt`.
- Da tao offline GraphRAG pipeline chay duoc khong can internet:
  - `scripts/extract_triples.py`
  - `scripts/build_graph.py`
  - `scripts/query_flat_rag.py`
  - `scripts/query_graphrag.py`
  - `scripts/run_benchmark.py`
  - `scripts/generate_report.py`
  - `scripts/run_lab.py`
- Da tao output:
  - `data/processed/chunks.jsonl`
  - `data/processed/triples.csv`
  - `data/processed/knowledge_graph.graphml`
  - `reports/figures/knowledge_graph_edges.txt`
  - `reports/benchmarks/results.csv`
  - `reports/benchmarks/summary.csv`
  - `reports/report.md`
- Benchmark hien tai:
  - Flat RAG accuracy: 70%
  - GraphRAG accuracy: 100%
  - Improvement: 30 percentage points, dat muc tieu >= 20%.

## 8. Lenh chay lai toan bo lab

Chay toan bo pipeline:

```powershell
.\.venv\Scripts\python.exe scripts\run_lab.py
```

Chay tung buoc:

```powershell
.\.venv\Scripts\python.exe scripts\extract_triples.py
.\.venv\Scripts\python.exe scripts\build_graph.py
.\.venv\Scripts\python.exe scripts\run_benchmark.py
.\.venv\Scripts\python.exe scripts\generate_report.py
```

Hoi GraphRAG:

```powershell
.\.venv\Scripts\python.exe scripts\query_graphrag.py "Which AI companies were co-founded by former Google employees?"
```

Hoi Flat RAG:

```powershell
.\.venv\Scripts\python.exe scripts\query_flat_rag.py "Which AI companies were co-founded by former Google employees?"
```

Kiem tra code:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m compileall src scripts tests
```

## 9. Viec can lam neu muon nang cap ban nop cuoi

- Neu can, thay corpus demo bang 10 bai Wikipedia/tom tat cong ty AI that.
- Thay rule-based extractor bang LLM extractor co JSON schema.
- Import `data/processed/triples.csv` vao Neo4j de chup visualization dep hon.
- Cap nhat `reports/benchmarks/questions.csv` bang ground truth tu corpus that.
- Rerun `scripts/run_lab.py` va cap nhat screenshot vao `reports/figures/`.
