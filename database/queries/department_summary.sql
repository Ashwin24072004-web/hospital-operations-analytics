SELECT
    d.department_name,
    COUNT(DISTINCT doc.doctor_id) AS doctor_count,
    COUNT(DISTINCT a.appointment_id) AS appointment_count,
    COUNT(DISTINCT CASE WHEN a.status = 'Completed' THEN a.appointment_id END) AS completed_count,
    COUNT(DISTINCT CASE WHEN a.status = 'No-show' THEN a.appointment_id END) AS no_show_count,
    COALESCE(SUM(p.amount_paid), 0) AS revenue
FROM departments d
LEFT JOIN doctors doc ON d.department_id = doc.department_id
LEFT JOIN appointments a
    ON doc.doctor_id = a.doctor_id
    AND a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
LEFT JOIN payments p ON t.treatment_id = p.treatment_id
WHERE (CAST(%(department_id)s AS INTEGER) IS NULL OR d.department_id = %(department_id)s)
GROUP BY d.department_id, d.department_name
ORDER BY appointment_count DESC, d.department_name;
