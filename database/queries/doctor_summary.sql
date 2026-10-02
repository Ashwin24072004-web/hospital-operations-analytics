SELECT
    doc.doctor_id,
    doc.doctor_name,
    doc.specialization,
    d.department_name,
    COUNT(DISTINCT a.appointment_id) AS appointment_count,
    COUNT(DISTINCT a.patient_id) AS unique_patients,
    COUNT(DISTINCT CASE WHEN a.status = 'Completed' THEN a.appointment_id END) AS completed_count,
    COALESCE(SUM(p.amount_paid), 0) AS revenue
FROM doctors doc
INNER JOIN departments d ON doc.department_id = d.department_id
LEFT JOIN appointments a
    ON doc.doctor_id = a.doctor_id
    AND a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
LEFT JOIN payments p ON t.treatment_id = p.treatment_id
WHERE (CAST(%(department_id)s AS INTEGER) IS NULL OR d.department_id = %(department_id)s)
  AND (CAST(%(doctor_id)s AS INTEGER) IS NULL OR doc.doctor_id = %(doctor_id)s)
GROUP BY doc.doctor_id, doc.doctor_name, doc.specialization, d.department_name
ORDER BY appointment_count DESC, doc.doctor_name;
