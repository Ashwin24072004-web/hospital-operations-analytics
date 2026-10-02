SELECT
    a.appointment_date,
    a.appointment_time,
    p.patient_name,
    doc.doctor_name,
    d.department_name,
    a.status
FROM appointments a
INNER JOIN patients p ON a.patient_id = p.patient_id
INNER JOIN doctors doc ON a.doctor_id = doc.doctor_id
INNER JOIN departments d ON doc.department_id = d.department_id
WHERE a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
ORDER BY a.appointment_date DESC, a.appointment_time DESC
LIMIT 20;

