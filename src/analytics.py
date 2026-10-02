from datetime import date
from typing import Any

import pandas as pd

from src.database import fetch_dataframe, fetch_value
from src.query_catalog import get_query


def _params(start_date: date, end_date: date, **extra: Any) -> dict[str, Any]:
    return {"start_date": start_date, "end_date": end_date, **extra}


def metric(query_id: str, start_date: date, end_date: date) -> int | float:
    value = fetch_value(get_query(query_id).sql, _params(start_date, end_date))
    return value or 0


def report(query_id: str, start_date: date, end_date: date, **filters: Any) -> pd.DataFrame:
    return fetch_dataframe(get_query(query_id).sql, _params(start_date, end_date, **filters))


def filter_options() -> dict[str, pd.DataFrame]:
    return {
        "departments": fetch_dataframe(
            "SELECT department_id, department_name FROM departments ORDER BY department_name"
        ),
        "doctors": fetch_dataframe(
            "SELECT doctor_id, doctor_name, department_id FROM doctors ORDER BY doctor_name"
        ),
        "cities": fetch_dataframe("SELECT DISTINCT city FROM patients ORDER BY city"),
        "dates": fetch_dataframe(
            "SELECT MIN(appointment_date) AS min_date, MAX(appointment_date) AS max_date FROM appointments"
        ),
    }


def patient_candidates(search: str, limit: int = 10) -> pd.DataFrame:
    """Find fictional patients for chatbot filter resolution."""
    if search.isdigit():
        return fetch_dataframe(
            """
            SELECT patient_id, patient_name, city
            FROM patients
            WHERE patient_id = %(patient_id)s
            ORDER BY patient_id
            LIMIT %(limit)s
            """,
            {"patient_id": int(search), "limit": limit},
        )
    return fetch_dataframe(
        """
        SELECT patient_id, patient_name, city
        FROM patients
        WHERE LOWER(patient_name) LIKE LOWER(%(patient_pattern)s)
        ORDER BY patient_name, patient_id
        LIMIT %(limit)s
        """,
        {"patient_pattern": f"%{search}%", "limit": limit},
    )
