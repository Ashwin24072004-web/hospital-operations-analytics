SELECT COALESCE(SUM(p.amount_paid), 0) AS total_revenue
FROM payments p
INNER JOIN treatments t ON p.treatment_id = t.treatment_id
INNER JOIN appointments a ON t.appointment_id = a.appointment_id
WHERE a.appointment_date BETWEEN %(start_date)s AND %(end_date)s;

