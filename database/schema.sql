DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name VARCHAR(80) UNIQUE NOT NULL,
    floor_number INTEGER NOT NULL CHECK (floor_number > 0)
);

CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY,
    doctor_name VARCHAR(120) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(department_id),
    hire_date DATE NOT NULL
);

CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    patient_name VARCHAR(120) NOT NULL,
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Female', 'Male', 'Non-binary')),
    date_of_birth DATE NOT NULL,
    city VARCHAR(80) NOT NULL,
    registration_date DATE NOT NULL
);

CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id INTEGER NOT NULL REFERENCES doctors(doctor_id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Completed', 'Scheduled', 'Cancelled', 'No-show')),
    reason VARCHAR(160) NOT NULL
);

CREATE TABLE treatments (
    treatment_id INTEGER PRIMARY KEY,
    appointment_id INTEGER NOT NULL REFERENCES appointments(appointment_id),
    treatment_name VARCHAR(120) NOT NULL,
    treatment_cost NUMERIC(10, 2) NOT NULL CHECK (treatment_cost >= 0),
    treatment_date DATE NOT NULL
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    treatment_id INTEGER NOT NULL REFERENCES treatments(treatment_id),
    amount_paid NUMERIC(10, 2) NOT NULL CHECK (amount_paid >= 0),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('Cash', 'Card', 'Insurance', 'Online')),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('Paid', 'Pending', 'Partially Paid')),
    payment_date DATE
);

CREATE INDEX appointments_date_idx ON appointments(appointment_date);
CREATE INDEX appointments_patient_idx ON appointments(patient_id);
CREATE INDEX appointments_doctor_idx ON appointments(doctor_id);
CREATE INDEX doctors_department_idx ON doctors(department_id);
CREATE INDEX treatments_appointment_idx ON treatments(appointment_id);
CREATE INDEX payments_treatment_idx ON payments(treatment_id);

COMMENT ON TABLE appointments IS 'One scheduled encounter between a fictional patient and doctor.';
COMMENT ON COLUMN appointments.status IS 'Completed, Scheduled, Cancelled, or No-show.';
COMMENT ON TABLE treatments IS 'Zero or more clinical services recorded for an appointment.';
COMMENT ON TABLE payments IS 'Payment outcome for a treatment; pending rows can have a null payment date.';

