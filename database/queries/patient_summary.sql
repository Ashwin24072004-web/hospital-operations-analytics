SELECT
    p.patient_id,
    p.patient_name,
    p.gender,
    p.city,
    COUNT(DISTINCT a.appointment_id) AS appointment_count,
    COALESCE(SUM(t.treatment_cost), 0) AS treatment_cost
FROM patients p
LEFT JOIN appointments a
    ON p.patient_id = a.patient_id
    AND a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
WHERE (CAST(%(city)s AS VARCHAR) IS NULL OR p.city = %(city)s)
  AND (%(patient_search)s = '' OR LOWER(p.patient_name) LIKE LOWER(%(patient_pattern)s))
GROUP BY p.patient_id, p.patient_name, p.gender, p.city
ORDER BY appointment_count DESC, p.patient_name
LIMIT 200;
