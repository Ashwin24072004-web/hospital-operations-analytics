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
- Optional Groq-powered RAG assistant using trusted, allowlisted SQL queries

## Run locally

Requirements:

- Python 3.11–3.13
- Git
- Docker Desktop or Docker Engine with Docker Compose v2

Docker Desktop must be running before the database commands are used. On Windows, use the Linux containers/WSL 2 backend.

### Windows PowerShell

From the cloned repository:

```powershell
Copy-Item .env.example .env
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
docker compose up -d --wait
python scripts/generate_data.py
python scripts/setup_database.py
python -m streamlit run app.py
```

The execution-policy command applies only to the current PowerShell window. If `py` is unavailable, use `python` instead.

### macOS or Linux

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
docker compose up -d --wait
python scripts/generate_data.py
python scripts/setup_database.py
python -m streamlit run app.py
```

Open the URL printed by Streamlit, normally <http://localhost:8501>.

### Enable the optional AI Assistant

The normal dashboard does not need an AI key. To enable chat, create a Groq API key and place a newly generated key in the local `.env` file:

```text
GROQ_API_KEY=your_new_key
GROQ_PRIMARY_MODEL=openai/gpt-oss-120b
GROQ_FALLBACK_MODEL=openai/gpt-oss-20b
```

Restart Streamlit after changing `.env`. Never commit the key. If a key is ever posted in a chat, screenshot, issue, or commit, revoke it and generate another one.

The model name prefix does not mean the application calls OpenAI's API. The Python client is pointed at Groq's OpenAI-compatible endpoint, and all requests go to Groq.

To stop PostgreSQL without deleting its data:

```bash
docker compose stop
```

To rebuild the database, rerun the data generator and setup script. The generator uses a fixed random seed, so it produces the same fictional dataset each time.

### Local troubleshooting

- If Docker reports that it cannot connect to the daemon, start Docker Desktop and rerun `docker compose up -d --wait`.
- If the selected Docker context is unavailable, run `docker context ls`, select an active context with `docker context use <name>`, and retry.
- PostgreSQL is exposed on local port `5433`. If that port is occupied, change the host-side port in `docker-compose.yml` and make the same change in `DATABASE_URL` inside `.env`.
- If database setup is rerun, `schema.sql` recreates the project tables and reloads the deterministic synthetic data.
- The AI Assistant requires internet access to Groq. All non-AI dashboard pages work offline after the Python packages and Docker image are installed.

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

## RAG assistant design

The optional AI Assistant uses:

- `knowledge/business_glossary.md` for metric definitions
- `knowledge/query_catalog.json` for local lexical retrieval and trusted query selection
- `database/queries/` for reviewed, parameterized SQL
- `src/analytics.py` as the execution boundary
- Groq GPT-OSS 120B for routing and grounded answers, with GPT-OSS 20B as fallback

The assistant retrieves five candidate reports, asks Groq to choose only among those IDs using strict structured output, validates every extracted filter in Python, and executes the selected query through the existing analytics layer. See `knowledge/rag_integration.md`.

The implemented assistant uses local lexical retrieval over the query catalog and glossary. Groq selects only among the retrieved query IDs using strict structured output. Python validates filters and executes the existing parameterized SQL; the model never creates or executes SQL. At most 25 database rows are supplied to the model for an answer, while the interface can show up to 100 matching rows.

## Run tests

```bash
python -m pytest -q
```

Tests mock Groq and do not consume API quota. They require the local PostgreSQL container for the Streamlit render check.

## Windows compatibility

The project is supported on Windows 10/11 with Docker Desktop and Python 3.11–3.13. Application paths use `pathlib`, PostgreSQL runs inside a Linux container, and database access uses `psycopg[binary]`, so no native PostgreSQL installation is required. The only platform-specific step is virtual-environment activation, which is documented above.

## Portfolio notes

All patient names and events are generated. No personal, clinical, or real hospital data is included. The app is read-only and parameterizes user-controlled filters.
