SELECT
    a.appointment_date,
    doc.doctor_name,
    d.department_name,
    a.status,
    a.reason,
    t.treatment_name,
    t.treatment_cost,
    pay.payment_status,
    pay.amount_paid
FROM appointments a
INNER JOIN doctors doc ON a.doctor_id = doc.doctor_id
INNER JOIN departments d ON doc.department_id = d.department_id
LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
LEFT JOIN payments pay ON t.treatment_id = pay.treatment_id
WHERE a.patient_id = %(patient_id)s
  AND a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
ORDER BY a.appointment_date DESC;

