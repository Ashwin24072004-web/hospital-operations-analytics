SELECT
    DATE_TRUNC('month', appointment_date)::date AS month,
    COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY DATE_TRUNC('month', appointment_date)
ORDER BY month;

