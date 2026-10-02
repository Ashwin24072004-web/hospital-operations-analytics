"""Generate deterministic, entirely fictional hospital data as CSV files."""

import csv
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RANDOM_SEED = 42

FIRST_NAMES = [
    "Aarav", "Aditi", "Ananya", "Arjun", "Diya", "Ishaan", "Kabir", "Kavya",
    "Meera", "Neha", "Nikhil", "Priya", "Rahul", "Riya", "Rohan", "Saanvi",
    "Sara", "Vihaan", "Vikram", "Zoya",
]
LAST_NAMES = [
    "Bansal", "Chopra", "Das", "Gupta", "Iyer", "Jain", "Kapoor", "Khan",
    "Malhotra", "Mehta", "Nair", "Patel", "Rao", "Shah", "Sharma", "Singh",
    "Verma", "Yadav",
]
CITIES = ["Bengaluru", "Chennai", "Delhi", "Hyderabad", "Jaipur", "Kolkata", "Mumbai", "Pune"]
DEPARTMENTS = [
    (1, "Cardiology", 2, "Cardiologist"),
    (2, "Dermatology", 3, "Dermatologist"),
    (3, "General Medicine", 1, "General Physician"),
    (4, "Neurology", 4, "Neurologist"),
    (5, "Orthopedics", 2, "Orthopedic Surgeon"),
    (6, "Pediatrics", 1, "Pediatrician"),
    (7, "ENT", 3, "ENT Specialist"),
    (8, "Ophthalmology", 4, "Ophthalmologist"),
]
REASONS = [
    "Routine consultation", "Follow-up visit", "Persistent pain", "Skin irritation",
    "Annual check-up", "Headache", "Vision concern", "Respiratory symptoms",
    "Child wellness visit", "Joint discomfort", "Hearing concern", "Test review",
]
TREATMENTS = [
    ("Consultation", 800, 1500),
    ("Blood test", 500, 1800),
    ("ECG", 1200, 2600),
    ("X-ray", 900, 2400),
    ("Ultrasound", 1600, 3500),
    ("Minor procedure", 2500, 7000),
    ("Physiotherapy session", 700, 1800),
    ("Vision examination", 600, 1400),
]


def random_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def write_csv(filename: str, headers: list[str], rows: list[tuple]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with (DATA_DIR / filename).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def generate() -> dict[str, int]:
    rng = random.Random(RANDOM_SEED)
    start_date = date(2024, 1, 1)
    end_date = date(2026, 9, 30)

    department_rows = [(item[0], item[1], item[2]) for item in DEPARTMENTS]

    doctor_rows = []
    for doctor_id in range(1, 36):
        department = DEPARTMENTS[(doctor_id - 1) % len(DEPARTMENTS)]
        name = f"Dr. {rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        hire_date = random_date(rng, date(2015, 1, 1), date(2023, 12, 31))
        doctor_rows.append((doctor_id, name, department[3], department[0], hire_date))

    patient_rows = []
    for patient_id in range(1, 1001):
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        gender = rng.choices(["Female", "Male", "Non-binary"], weights=[49, 49, 2])[0]
        birth_date = random_date(rng, date(1945, 1, 1), date(2020, 12, 31))
        registration_date = random_date(rng, date(2022, 1, 1), end_date)
        patient_rows.append(
            (patient_id, name, gender, birth_date, rng.choice(CITIES), registration_date)
        )

    appointment_rows = []
    appointment_status: dict[int, str] = {}
    appointment_date: dict[int, date] = {}
    for appointment_id in range(1, 5001):
        patient_id = rng.randint(1, 900)  # Leaves 100 patients with no appointments.
        doctor_id = rng.randint(1, len(doctor_rows))
        visit_date = random_date(rng, start_date, end_date)
        visit_time = time(rng.randint(8, 18), rng.choice([0, 15, 30, 45]))
        status = rng.choices(
            ["Completed", "Scheduled", "Cancelled", "No-show"],
            weights=[68, 12, 12, 8],
        )[0]
        appointment_rows.append(
            (appointment_id, patient_id, doctor_id, visit_date, visit_time, status, rng.choice(REASONS))
        )
        appointment_status[appointment_id] = status
        appointment_date[appointment_id] = visit_date

    treatment_rows = []
    treatment_id = 1
    completed_ids = [item[0] for item in appointment_rows if item[5] == "Completed"]
    rng.shuffle(completed_ids)
    for appointment_id in completed_ids:
        if rng.random() > 0.86:
            continue  # Meaningful appointments-without-treatment LEFT JOIN cases.
        treatment_count = 2 if rng.random() < 0.18 else 1
        for _ in range(treatment_count):
            name, minimum, maximum = rng.choice(TREATMENTS)
            cost = rng.randrange(minimum, maximum + 1, 50)
            treatment_rows.append(
                (treatment_id, appointment_id, name, f"{cost:.2f}", appointment_date[appointment_id])
            )
            treatment_id += 1

    payment_rows = []
    for payment_id, treatment in enumerate(treatment_rows, start=1):
        current_treatment_id = treatment[0]
        cost = float(treatment[3])
        payment_status = rng.choices(
            ["Paid", "Pending", "Partially Paid"], weights=[78, 12, 10]
        )[0]
        if payment_status == "Paid":
            amount = cost
            paid_date = appointment_date[treatment[1]] + timedelta(days=rng.randint(0, 14))
        elif payment_status == "Partially Paid":
            amount = round(cost * rng.choice([0.25, 0.5, 0.75]), 2)
            paid_date = appointment_date[treatment[1]] + timedelta(days=rng.randint(0, 14))
        else:
            amount = 0
            paid_date = ""
        payment_rows.append(
            (
                payment_id,
                current_treatment_id,
                f"{amount:.2f}",
                rng.choice(["Cash", "Card", "Insurance", "Online"]),
                payment_status,
                paid_date,
            )
        )

    write_csv("departments.csv", ["department_id", "department_name", "floor_number"], department_rows)
    write_csv(
        "doctors.csv",
        ["doctor_id", "doctor_name", "specialization", "department_id", "hire_date"],
        doctor_rows,
    )
    write_csv(
        "patients.csv",
        ["patient_id", "patient_name", "gender", "date_of_birth", "city", "registration_date"],
        patient_rows,
    )
    write_csv(
        "appointments.csv",
        ["appointment_id", "patient_id", "doctor_id", "appointment_date", "appointment_time", "status", "reason"],
        appointment_rows,
    )
    write_csv(
        "treatments.csv",
        ["treatment_id", "appointment_id", "treatment_name", "treatment_cost", "treatment_date"],
        treatment_rows,
    )
    write_csv(
        "payments.csv",
        ["payment_id", "treatment_id", "amount_paid", "payment_method", "payment_status", "payment_date"],
        payment_rows,
    )

    return {
        "departments": len(department_rows),
        "doctors": len(doctor_rows),
        "patients": len(patient_rows),
        "appointments": len(appointment_rows),
        "treatments": len(treatment_rows),
        "payments": len(payment_rows),
    }


if __name__ == "__main__":
    counts = generate()
    print("Generated deterministic synthetic data:")
    for table, count in counts.items():
        print(f"  {table}: {count:,}")
