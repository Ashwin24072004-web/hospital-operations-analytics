SELECT d.department_name, COUNT(a.appointment_id) AS appointment_count
FROM departments d
LEFT JOIN doctors doc ON d.department_id = doc.department_id
LEFT JOIN appointments a
    ON doc.doctor_id = a.doctor_id
    AND a.appointment_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY d.department_id, d.department_name
ORDER BY appointment_count DESC, d.department_name;

