# Future RAG integration contract

The current application does not call an AI model. It prepares a safe, stable boundary for one.

## Trusted retrieval sources

1. `business_glossary.md` defines business terms.
2. `query_catalog.json` maps natural-language questions and keywords to reviewed query IDs.
3. `database/queries/*.sql` contains the allowlisted SQL.
4. `database/schema.sql` documents entities and relationships.

## Recommended chatbot flow

1. Retrieve relevant glossary and query-catalog entries for the user's question.
2. Select an existing `query_id`; do not let the model write arbitrary SQL in the first version.
3. Validate required filters such as date range, department, doctor, or patient.
4. Execute through `src.analytics.report()` or `src.analytics.metric()` using parameters.
5. Give the returned rows to the model as structured context.
6. Generate an answer that cites the query title and active filters.

## Safety boundaries

- Connect with a read-only PostgreSQL user in any deployed version.
- Keep synthetic data clearly labelled.
- Allow only `SELECT` queries from the trusted catalog.
- Limit returned rows before sending context to a model.
- Never place database credentials or sensitive rows in prompts or logs.

This design supports later use with LangChain, LlamaIndex, or a small custom retrieval layer without coupling the analytics application to one framework today.
