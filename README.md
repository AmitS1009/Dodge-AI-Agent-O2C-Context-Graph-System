# 🚀 Dodge AI Agent | O2C Context Graph System

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Google Gemini Pro 1.5](https://img.shields.io/badge/LLM-Gemini_Pro_1.5-orange.svg)](https://ai.google.dev/)
[![FastAPIu(https://img.shields.io/badge/Framework-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg?logo=sqlite)](https://sqlite.org/)

> **A production-ready Enterprise Knowledge Graph & LLM Engine** transforming complex, globally distributed SAP Order-to-Cash (O2C) logistics data into conversational, instantly accessible supply chain intelligence.

## 🌕 High-Impact Outcomes
*   **Zero-to-Insight:** Replaced days of manual SQL/SAP reporting with natural language conversational querying.
*   **Architectural Simplicity at Scale:** Engineered an embedded, zero-config Graph abstraction layer directly over massively partitioned flat files (JSONL) via local SQLite/Pandas pipelines.
*   **Deterministic Reliability:** Integrated strict LLM guardrails (dynamic schema reflection + rigid topic conditioning) to guarantee purely deterministic, hallucination-free business reporting.

## ️ System Architecture

Our custom Graph Abstraction Layer resolves relationships between `SalesOrders`, `Deliveries`, `Billings`, and `JournalEntries` on-the-fly, serving interactive topological maps via Vis.js.

```mermaid
graph TD
    #% User Interaction
    User[User natural language query] -->|HTTP / API| FastAPI[FastAPI Backend]
    
    #% Backend LLM Logic
    FastAPI --> LLMProxy[LLM Orchestrator<br>Gemini Pro 1.5]
    LLMProxy -.->|Check Guardrails| TopicFilter{Topic Validation}
    TopicFilter -->|REJECT| Error[Halt & Return Guardrail msg]
    TopicFilter -->|PASS| SQLGen[Schema-aware SQL Translator]
    
    #% Data Pipeline
    JSONL[(SAP JSONL Data<br>Millions of Rows)] -->|Parser: build_db.py| SQLite[(SQLite O2C Database)]
    
    #% Execution & UI
    SQLGen -->|Executes SQLite Query| SQLite
    SQLite -->|Raw Result| LLMProxy
    LLMProxy -->|Synthesize Natural Lang| User
    
    #% Graph Vis
    SQLite -->|Graph Resolvers: graph.py| VisJS{{Vis.js Visualizer}}
    VisJS -->|Interactive topology| User
```

## 🤝 Core Engineering Principles

1.  **Lightweight & Zero-Config:** Eschewed heavy graph-native DBs (like Neo4j) for embedded **SQLite + Dynamic Graph Abstraction*, delivering instantaneous local deployment without infrastructural bloat.
2.  **RAG meets Graph:** Fuses generative intelligence with strict referential data validation. The LLM acts purely as a linguistic to logical-SQL compiler (`text2sql`).
3.  **Strict Security Guardrails:** Model input and output are sandboxed to specific logistics domains (O2C). Out-of-bounds queries immediately hit a hard `REJECT` boundary.
4.  **Performant Data Ingestion:** Vectorized `Pandas` parsers seamlessly join & commit disjointed temporal partitions into highly indexed, relational tables.

---

## ⚼️ Quick Start
**Prerequisites**: Python 3.9+ | `.env` file containing `GEMINI_API_KEY=your_key` | Unzipped `sap-o2c-data` directory.

### 1. Build the Engine
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/build_db.py
```
*(Automated ETL pipeline ingesting distributed JSONL payloads into normalized SQL tables).*

### 2. Ignite the Server
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```
**Access the interface at** `http://localhost:8000` to interact with the LLM data copilot and visualize the supply chain context graph.