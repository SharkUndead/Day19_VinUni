# Bao cao tong hop Lab Day 19: GraphRAG voi Tech Company Corpus

## 1. De bai yeu cau gi?

Lab Day 19 yeu cau xay dung mot he thong GraphRAG tren tap du lieu ve cac cong ty cong nghe/AI. Muc tieu chinh khong chi la hoi dap bang RAG thong thuong, ma la tao duoc mot Knowledge Graph de ho tro cac cau hoi can suy luan nhieu buoc.

Noi dung de bai co cac yeu cau lon:

1. Nghien cuu quy trinh GraphRAG:
   - Trich xuat thuc the, goi la entity/node.
   - Trich xuat quan he, goi la relation/edge.
   - Tao triples dang `(subject, predicate, object)`.
   - Xay dung graph tu cac triples.
   - Truy van graph bang BFS/multi-hop.

2. Lam quen voi cac cong cu:
   - NetworkX: dung de prototype graph nhanh trong Python.
   - Neo4j: dung de luu graph va truc quan hoa.
   - NodeRAG: framework ho tro GraphRAG.

3. Xay dung pipeline GraphRAG:
   - Doc corpus.
   - Trich xuat triples.
   - Xay dung Knowledge Graph.
   - Tim seed node tu cau hoi.
   - Duyet graph trong pham vi 2-hop.
   - Chuyen subgraph thanh text context.
   - Tao cau tra loi dua tren context.

4. So sanh voi Flat RAG:
   - Flat RAG chi retrieve text/chunks.
   - GraphRAG retrieve theo quan he trong graph.
   - Benchmark toi thieu 20 cau hoi, tap trung vao cau hoi multi-hop.

5. Deliverables can nop:
   - Source code `.py` hoac notebook.
   - Visualization cua Knowledge Graph.
   - Bang benchmark so sanh Flat RAG va GraphRAG.
   - Phan tich accuracy, latency, cost/token usage.
   - Phan tich cac truong hop Flat RAG sai nhung GraphRAG dung.

## 2. Dieu chinh pham vi bai lam

Ban da noi khong can 100 bai Wikipedia, chi can khoang 10 bai cung duoc. Vi vay bai lam hien tai dung mot corpus demo gom 12 tom tat ve cac cong ty AI/cong nghe.

Corpus nam tai:

```text
data/raw/tech_company_corpus.txt
```

Corpus co cac entity/cong ty nhu:

- OpenAI
- Anthropic
- DeepMind
- Google
- Microsoft
- Meta
- xAI
- Inflection AI
- Cohere
- Character AI
- Perplexity AI
- Nvidia

Ly do dung 12 muc thay vi dung dung 10 muc: co them mot vai cong ty giup benchmark phong phu hon, nhung van nam trong pham vi nho, de giai thich va de chay offline.

## 3. Kien truc da xay dung

Project da duoc chia thanh cac phan ro rang:

```text
data/raw/                         # Corpus goc
data/processed/                   # Chunks, triples, graph export
src/graphrag_lab/                 # Source code chinh
scripts/                          # Cac script chay pipeline
reports/benchmarks/               # Cau hoi, ket qua, summary benchmark
reports/figures/                  # Visualization/text graph
reports/report.md                 # Bao cao benchmark tu dong
```

Cac file quan trong:

```text
src/graphrag_lab/extraction.py    # Trich xuat triples
src/graphrag_lab/graph.py         # Knowledge Graph va BFS
src/graphrag_lab/flat_rag.py      # Flat RAG baseline
src/graphrag_lab/graphrag.py      # GraphRAG answering
src/graphrag_lab/benchmark.py     # Chay benchmark
src/graphrag_lab/costing.py       # Uoc tinh chi phi API
src/graphrag_lab/llm.py           # Goi OpenAI/Groq neu co API key
src/graphrag_lab/llm_extraction.py # LLM-based NER optional
src/graphrag_lab/embeddings.py    # Tao node embeddings local
scripts/run_lab.py                # Chay toan bo pipeline
```

## 4. Pipeline da lam duoc

### Buoc 1: Doc corpus va tao chunks

Script doc corpus tu:

```text
data/raw/tech_company_corpus.txt
```

Sau do tach thanh 12 chunks va ghi ra:

```text
data/processed/chunks.jsonl
```

Ket qua:

```text
Wrote 12 chunks
```

Ly do lam buoc nay: Flat RAG va GraphRAG deu can mot don vi du lieu dau vao. Chunk giup mo phong cach RAG xu ly tai lieu dai.

### Buoc 2: Trich xuat triples

He thong trich xuat triples dang:

```text
subject,predicate,object
```

Vi du:

```text
OpenAI,FOUNDED_BY,Sam Altman
OpenAI,PARTNERED_WITH,Microsoft
Google,ACQUIRED,DeepMind
Aidan Gomez,FORMERLY_WORKED_AT,Google
Cohere,FOUNDED_BY,Aidan Gomez
```

Output:

```text
data/processed/triples.csv
```

Ket qua:

```text
Wrote 105 triples
```

Ly do lam the nay: Knowledge Graph can cac canh co cau truc. Triple la cach bieu dien don gian va de import sang NetworkX/Neo4j.

Ngoai ban offline rule-based, project da co them script LLM-based NER:

```powershell
python scripts\extract_triples_llm.py --provider openai
python scripts\extract_triples_llm.py --provider groq
```

Khuyen dung OpenAI cho ban nop cuoi neu can JSON on dinh. Groq phu hop de thu nghiem nhanh va tiet kiem chi phi.

### Buoc 3: Xay dung Knowledge Graph

Tu 105 triples, he thong tao graph:

```text
Graph nodes: 84
Graph edges: 105
```

Output:

```text
data/processed/knowledge_graph.graphml
reports/figures/knowledge_graph_edges.txt
reports/figures/knowledge_graph.svg
```

Ly do dung GraphML: day la dinh dang pho bien, co the mo bang cong cu graph visualization nhu Gephi, yEd, hoac import vao Neo4j sau.

Project cung co script visualization:

```powershell
python scripts\generate_visualization.py
```

Neu may da cai `networkx` va `matplotlib`, script se xuat:

```text
reports/figures/knowledge_graph_networkx.png
```

Neu chua cai, script tu dong tao SVG fallback:

```text
reports/figures/knowledge_graph.svg
reports/figures/knowledge_graph.html
```

### Buoc 3.5: Them node embeddings

Project da tao node embeddings local tu neighborhood cua moi node.

Output:

```text
data/embeddings/node_embeddings.json
data/embeddings/node_similarity.csv
```

Ly do lam the nay: de dap ung yeu cau "them embeddings cho nodes". Trong ban offline, embeddings la local hashed vectors, khong ton API cost. Neu can ban production, co the thay bang OpenAI embeddings hoac embedding model khac.

### Buoc 4: Xay dung Flat RAG baseline

Flat RAG trong bai nay la baseline don gian:

1. Tokenize cau hoi.
2. Tim chunks co nhieu tu trung voi cau hoi.
3. Lay top-k chunks.
4. Sinh cau tra loi tu cac cau gan nhat.

Ly do can Flat RAG: de co moc so sanh voi GraphRAG. De bai yeu cau chung minh GraphRAG tot hon trong cau hoi multi-hop.

### Buoc 5: Xay dung GraphRAG

GraphRAG pipeline:

1. Nhan cau hoi.
2. Tim seed nodes trong graph.
3. BFS traversal trong pham vi 2-hop.
4. Lay cac triples lien quan.
5. Textualize subgraph.
6. Tong hop cau tra loi.

Vi du cau hoi:

```text
Which AI companies were co-founded by former Google employees?
```

GraphRAG tim duoc chuoi quan he:

```text
Aidan Gomez --FORMERLY_WORKED_AT--> Google
Cohere --FOUNDED_BY--> Aidan Gomez

Noam Shazeer --FORMERLY_WORKED_AT--> Google
Character AI --FOUNDED_BY--> Noam Shazeer
```

Nen tra loi:

```text
AI companies co-founded by former Google employees include Character AI, Cohere.
```

Ly do GraphRAG lam tot cau nay: cau hoi can noi hai quan he:

```text
former Google employee -> founded/co-founded company
```

Flat RAG chi tim text gan nghia nen de lay sai context.

## 5. Benchmark da thuc hien

Benchmark gom 20 cau hoi:

```text
reports/benchmarks/questions.csv
```

Ket qua chi tiet:

```text
reports/benchmarks/results.csv
```

Tong hop:

```text
reports/benchmarks/summary.csv
```

Ket qua hien tai:

```text
Flat RAG accuracy: 70%
GraphRAG accuracy: 100%
Improvement: 30 percentage points
```

Dieu nay dat muc tieu de bai vi GraphRAG cao hon Flat RAG tren 20 diem phan tram.

## 6. Vi sao Flat RAG sai trong mot so cau?

Flat RAG chi dua vao do trung khop text. No khong that su biet rang:

```text
A worked at Google
A founded Company X
=> Company X la cong ty duoc founder cuu nhan vien Google lap ra
```

Vi du voi cau hoi:

```text
Which AI companies were co-founded by former Google employees?
```

Flat RAG tra loi:

```text
Mustafa Suleyman co-founded DeepMind...
Inflection AI was founded by Mustafa Suleyman...
```

Cau nay bi lech vi no thay cac tu lien quan nhu `co-founded`, `AI`, `employees`, nhung khong noi dung logic `former Google employees`.

GraphRAG tra loi dung vi no di theo canh trong graph.

## 7. Chi phi API duoc uoc tinh nhu the nao?

Bai hien tai chay offline, khong goi API that. Tuy nhien da them phan uoc tinh chi phi gia dinh trong:

```text
src/graphrag_lab/costing.py
reports/report.md
reports/benchmarks/summary.csv
```

Gia dinh:

```text
Model: gpt-4.1-mini
Input:  $0.40 / 1M tokens
Output: $1.60 / 1M tokens
Token estimate: 1 token ~= 4 ky tu
```

Ket qua uoc tinh:

```text
Triple extraction/indexing: $0.001653
20 Flat RAG answer calls:  $0.002436
20 GraphRAG answer calls:  $0.003825
Total GraphRAG pipeline:  $0.005478
```

Ly do GraphRAG query cost cao hon Flat RAG mot chut: GraphRAG dua graph context vao prompt, context co cau truc hon nhung co the dai hon.

Ly do van nen dung GraphRAG: chi phi tang nho, nhung accuracy tren benchmark tang tu 70% len 100%.

## 8. Cach chay lai bai lab

Kich hoat venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

Chay toan bo pipeline:

```powershell
python scripts\run_lab.py
```

Kiem tra benchmark summary:

```powershell
Get-Content reports\benchmarks\summary.csv
```

Chay test:

```powershell
python -m unittest discover -s tests
```

Hoi GraphRAG:

```powershell
python scripts\query_graphrag.py "Which AI companies were co-founded by former Google employees?"
```

Hoi Flat RAG:

```powershell
python scripts\query_flat_rag.py "Which AI companies were co-founded by former Google employees?"
```

## 9. Nhung gi da hoan thanh so voi yeu cau

| Yeu cau | Trang thai |
| --- | --- |
| Tao corpus cong ty AI | Da co 12 tom tat |
| Trich xuat entity/relation | Da co 105 triples |
| Build Knowledge Graph | Da co 84 nodes, 105 edges |
| Them embeddings cho nodes | Da co local node embeddings |
| Graph traversal 2-hop | Da co trong GraphRAG |
| Flat RAG baseline | Da co |
| Benchmark 20 cau hoi | Da co |
| Accuracy comparison | Da co |
| Cost estimate | Da co |
| Visualization/export graph | Da co GraphML, text edges, SVG/HTML fallback; PNG NetworkX neu cai du thu vien |
| Report | Da co `reports/report.md` va file tong hop nay |

