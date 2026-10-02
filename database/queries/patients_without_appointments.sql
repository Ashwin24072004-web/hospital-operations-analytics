SELECT p.patient_id, p.patient_name, p.city, p.registration_date
FROM patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
WHERE a.appointment_id IS NULL
ORDER BY p.registration_date DESC;
