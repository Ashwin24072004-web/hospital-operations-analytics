# Hospital Operations Analytics

A local, resume-ready SQL portfolio project built with PostgreSQL, Python, and Streamlit. It analyzes entirely synthetic hospital operations through fundamental SQL, aggregate functions, `INNER JOIN`, and `LEFT JOIN`.

The codebase is also prepared for a future RAG chatbot: business definitions and reviewed analytical queries are stored as retrievable knowledge, and database access is kept separate from the UI.

## What the dashboard answers

- How appointment demand changes over time
- Which departments and doctors handle the most visits
- How completed, cancelled, scheduled, and no-show visits compare
- Which treatments generated collected revenue
- Which patients have no appointments
- Which treatments have an outstanding payment

## Technology

- PostgreSQL 15 in Docker, exposed on local port 5433 to avoid common port conflicts
- Python 3.11+
- Streamlit, Pandas, Plotly, and Psycopg 3
- Deterministic synthetic CSV generation using the Python standard library

## Run locally

Requirements: Python 3.11 or newer, Docker, and Docker Compose.

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker --context default compose up -d
python scripts/generate_data.py
python scripts/setup_database.py
streamlit run app.py
```

Open the URL printed by Streamlit, normally <http://localhost:8501>.

To stop PostgreSQL without deleting its data:

```bash
docker --context default compose stop
```

To rebuild the database, rerun the data generator and setup script. The generator uses a fixed random seed, so it produces the same fictional dataset each time.

## Database model

```text
departments 1 ─── many doctors
doctors     1 ─── many appointments
patients    1 ─── many appointments
appointments 1 ─── many treatments
treatments   1 ─── many payments
```

The six-table schema is defined in `database/schema.sql`. Query files live in `database/queries/` so the SQL remains visible and independently reviewable.

## SQL scope

The project intentionally stays within beginner/intermediate SQL:

- Filtering, sorting, and limiting
- `COUNT`, `SUM`, and `COALESCE`
- `GROUP BY`
- `CASE`
- `INNER JOIN` and `LEFT JOIN`
- Basic PostgreSQL date grouping

It does not use CTEs, window functions, stored procedures, or model-generated SQL.

## RAG-ready design

The current release contains no AI dependency. A future chatbot can reuse:

- `knowledge/business_glossary.md` for metric definitions
- `knowledge/query_catalog.json` for semantic retrieval and trusted query selection
- `database/queries/` for reviewed, parameterized SQL
- `src/analytics.py` as the execution boundary

The recommended design is retrieval over an allowlist: map a user's question to a catalog query ID, execute that query with validated parameters, and give the result to the model as context. See `knowledge/rag_integration.md`.

## Run tests

```bash
pytest -q
```

## Portfolio notes

All patient names and events are generated. No personal, clinical, or real hospital data is included. The app is read-only and parameterizes user-controlled filters.
