# Future RAG integration contract

The optional AI Assistant calls Groq through its OpenAI-compatible endpoint. The normal dashboard remains usable without an API key.

## Trusted retrieval sources

1. `business_glossary.md` defines business terms.
2. `query_catalog.json` maps natural-language questions and keywords to reviewed query IDs.
3. `database/queries/*.sql` contains the allowlisted SQL.
4. `database/schema.sql` documents entities and relationships.

## Recommended chatbot flow

1. Rank relevant glossary and query-catalog entries locally using weighted lexical matching.
2. Let Groq select only among the five retrieved `query_id` values using strict structured output; never let the model write SQL.
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

The implementation deliberately avoids LangChain, LlamaIndex, embeddings, and a vector database. The small trusted corpus does not require them yet.
