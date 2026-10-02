import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.query_catalog import QueryDefinition, load_catalog


ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_PATH = ROOT / "knowledge" / "business_glossary.md"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "by", "for", "from", "has", "have", "how",
    "in", "is", "of", "on", "or", "the", "to", "was", "were", "what",
    "which", "who", "with",
}


@dataclass(frozen=True)
class RetrievedQuery:
    definition: QueryDefinition
    score: int


@dataclass(frozen=True)
class GlossarySection:
    title: str
    content: str
    score: int = 0


def tokenize(text: str) -> set[str]:
    return {token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS}


def _overlap(question_tokens: set[str], text: str) -> int:
    return len(question_tokens.intersection(tokenize(text)))


def rank_queries(question: str, limit: int = 5) -> list[RetrievedQuery]:
    """Rank trusted queries locally without embeddings or an API call."""
    question_tokens = tokenize(question)
    ranked: list[RetrievedQuery] = []
    for definition in load_catalog().values():
        score = 0
        score += 4 * _overlap(question_tokens, f"{definition.title} {definition.question}")
        score += 2 * _overlap(question_tokens, " ".join(definition.keywords))
        score += _overlap(
            question_tokens,
            f"{' '.join(definition.entities)} {definition.explanation} {definition.result_description}",
        )
        ranked.append(RetrievedQuery(definition=definition, score=score))
    ranked.sort(key=lambda item: (-item.score, item.definition.query_id))
    return ranked[:limit]


@lru_cache(maxsize=1)
def load_glossary_sections() -> tuple[GlossarySection, ...]:
    text = GLOSSARY_PATH.read_text(encoding="utf-8")
    sections: list[GlossarySection] = []
    current_title = "Overview"
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append(
                    GlossarySection(current_title, "\n".join(current_lines).strip())
                )
            current_title = line[3:].strip()
            current_lines = []
        elif not line.startswith("# "):
            current_lines.append(line)
    if current_lines:
        sections.append(GlossarySection(current_title, "\n".join(current_lines).strip()))
    return tuple(section for section in sections if section.content)


def rank_glossary(question: str, limit: int = 3) -> list[GlossarySection]:
    question_tokens = tokenize(question)
    ranked = [
        GlossarySection(
            title=section.title,
            content=section.content,
            score=3 * _overlap(question_tokens, section.title)
            + _overlap(question_tokens, section.content),
        )
        for section in load_glossary_sections()
    ]
    ranked.sort(key=lambda item: (-item.score, item.title))
    return ranked[:limit]
