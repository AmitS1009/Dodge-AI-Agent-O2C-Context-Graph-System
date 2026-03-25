# Order-to-Cash Context Graph System

## Overview
This system is designed to parse an SAP Order-to-Cash (O2C) dataset and unifies the fragmented data—Sales Orders, Deliveries, Invoices, Payments—into a connected graph. It integrates a conversational LLM interface that dynamically generates SQL queries to answer natural language questions about the underlying data.

## Demo
Please enter your valid GEMINI_API_KEY in the `.env` file and simply run the application. Accessible via `http://localhost:8000`.

## Architecture Decisions

### 1. Database Choice: Local SQLite In-Memory / File-based SQLite
We chose **SQLite** combined with Pandas `to_sql` parser.
- **Why?**: The data is partitioned across multiple JSONL files which are intrinsically relational (e.g. `referenceSDDocument` joins to `salesOrder`). SQLite makes it seamlessly fast to translate natural language into SQL using an LLM. Pure graph databases like Neo4j are powerful but require user-side infrastructure setup mapping. SQLite allows you to run this out-of-the-box locally. We compute the **graph relations on-the-fly** by logically abstracting graph paths over relational SQL.

### 2. Graph Construction and Visualization
- **Backend Graph Resolution (`graph.py`)**: Models entities such as `SalesOrder`, `Delivery`, `Billing`, `JournalEntry` as abstract nodes. Calling `/api/graph/expand/...` performs explicit SQL joins to resolve edges.
- **Frontend Visualization (`vis-network.js`)**: A lightweight visualization library that draws dynamic, expandable networks. Nodes can be clicked to load rich metadata payloads and you can sequentially expand the supply chain without loading millions of nodes at once. 

### 3. LLM Integration and Prompting Strategy (`llm.py`)
Model Used: **Google Gemini Pro 1.5**
- **Architecture Flow**:
  1. The user asks a natural language question.
  2. The LLM gets a `SCHEMA_INSTRUCTIONS` prompt detailing the SAP O2C database structure and foreign key mappings.
  3. The LLM translates the query dynamically into a `raw SQLite query`.
  4. The code executes the resulting query securely against the `o2c.db` file dataset.
  5. The query results are passed back to the LLM again to synthesize a highly accurate, data-backed natural language response.

### 4. Guardrails
The prompt enforces strict topic conditioning.
- **Rules Triggered**: The system is explicitly instructed that if a user prompt does not pertain to SAP, O2C, Orders, Deliveries, Customers, or Sales, it must return exactly: `"REJECT"`.
- If "REJECT" is matched, the backend gracefully halts execution and returns a pre-canned response: `"This system is designed to answer questions related to the provided dataset only."`

## Setup and Installation

### 1. Requirements
- Python 3.9+
- A Google Gemini API Key

### 2. Environment Variables
Create a `.env` file in the root of the project with the following:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start Backend & UI Layer
Make sure you have unzipped the SAP dataset into an `sap-o2c-data` folder in the root path.

1. **Setup python env**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Ingest the Database**
Run the parser one-time to generate `o2c.db` from jsonl files:
```bash
python src/build_db.py
```
*(This script iterates all files in `sap-o2c-data` and ingests them into tabular SQLite formats, extracting node relationships).*

3. **Start the API System**
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```
Then visit `http://localhost:8000` to interact with the LLM and the Context Graph.
