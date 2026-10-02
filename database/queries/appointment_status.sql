SELECT status, COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY status
ORDER BY appointment_count DESC;

