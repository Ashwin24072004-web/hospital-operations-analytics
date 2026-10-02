"""Create the schema and bulk-load generated CSV data into PostgreSQL."""

from pathlib import Path
import sys

import psycopg

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import database_url


TABLES = ["departments", "doctors", "patients", "appointments", "treatments", "payments"]


def setup() -> None:
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    with psycopg.connect(database_url()) as connection:
        connection.execute(schema)
        for table in TABLES:
            csv_path = ROOT / "data" / f"{table}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Missing {csv_path}. Run 'python scripts/generate_data.py' first."
                )
            with csv_path.open("r", encoding="utf-8") as handle:
                with connection.cursor().copy(
                    f"COPY {table} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
                ) as copy:
                    while chunk := handle.read(1024 * 1024):
                        copy.write(chunk)
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Loaded {table}: {count:,} rows")
    print("Database setup complete.")


if __name__ == "__main__":
    setup()
