SELECT COUNT(*) AS total_appointments
FROM appointments
WHERE appointment_date BETWEEN %(start_date)s AND %(end_date)s;

