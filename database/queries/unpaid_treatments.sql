SELECT
    p.patient_name,
    t.treatment_name,
    t.treatment_cost,
    pay.amount_paid,
    pay.payment_status,
    a.appointment_date
FROM treatments t
INNER JOIN appointments a ON t.appointment_id = a.appointment_id
INNER JOIN patients p ON a.patient_id = p.patient_id
LEFT JOIN payments pay ON t.treatment_id = pay.treatment_id
WHERE a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
  AND (pay.payment_status IS NULL OR pay.payment_status <> 'Paid')
ORDER BY a.appointment_date DESC;

