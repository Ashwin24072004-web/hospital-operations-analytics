import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "database" / "queries"
CATALOG_PATH = ROOT / "knowledge" / "query_catalog.json"


@dataclass(frozen=True)
class QueryDefinition:
    query_id: str
    title: str
    question: str
    sql_file: str
    entities: tuple[str, ...]
    join_type: str
    explanation: str
    keywords: tuple[str, ...]

    @property
    def sql(self) -> str:
        return (QUERY_DIR / self.sql_file).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, QueryDefinition]:
    """Load trusted analytics metadata reusable by the UI and a future RAG layer."""
    raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {
        item["query_id"]: QueryDefinition(
            query_id=item["query_id"],
            title=item["title"],
            question=item["question"],
            sql_file=item["sql_file"],
            entities=tuple(item["entities"]),
            join_type=item["join_type"],
            explanation=item["explanation"],
            keywords=tuple(item["keywords"]),
        )
        for item in raw
    }


def get_query(query_id: str) -> QueryDefinition:
    try:
        return load_catalog()[query_id]
    except KeyError as exc:
        raise KeyError(f"Unknown trusted query: {query_id}") from exc

