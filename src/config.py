import os

from dotenv import load_dotenv


load_dotenv()


def database_url() -> str:
    """Return the configured PostgreSQL URL or the local development default."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://hospital_user:hospital_password@localhost:5433/hospital_analytics",
    )


def groq_api_key() -> str | None:
    """Return the Groq key without logging or exposing it."""
    return os.getenv("GROQ_API_KEY") or None


def groq_base_url() -> str:
    return os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")


def groq_primary_model() -> str:
    return os.getenv("GROQ_PRIMARY_MODEL", "openai/gpt-oss-120b")


def groq_fallback_model() -> str:
    return os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
