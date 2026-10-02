import os

from dotenv import load_dotenv


load_dotenv()


def database_url() -> str:
    """Return the configured PostgreSQL URL or the local development default."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://hospital_user:hospital_password@localhost:5433/hospital_analytics",
    )
