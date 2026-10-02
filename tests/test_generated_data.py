import csv
from pathlib import Path

from scripts.generate_data import DATA_DIR, generate


def row_count(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def test_generator_creates_expected_core_counts():
    counts = generate()
    assert counts["departments"] == 8
    assert counts["doctors"] == 35
    assert counts["patients"] == 1000
    assert counts["appointments"] == 5000
    assert row_count(DATA_DIR / "patients.csv") == 1000
    assert row_count(DATA_DIR / "appointments.csv") == 5000


def test_last_hundred_patients_have_no_appointments():
    generate()
    with (DATA_DIR / "appointments.csv").open(encoding="utf-8") as handle:
        used_patient_ids = {int(row["patient_id"]) for row in csv.DictReader(handle)}
    assert not used_patient_ids.intersection(range(901, 1001))

