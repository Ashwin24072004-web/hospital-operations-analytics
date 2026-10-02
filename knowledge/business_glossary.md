# Hospital analytics business glossary

All people and events in this project are synthetic. Nothing represents a real patient.

## Metrics

- **Appointment count:** Number of rows in `appointments` in the selected date range.
- **Completed appointment:** Appointment whose `status` is `Completed`.
- **No-show:** Appointment whose `status` is `No-show`.
- **Unique patients:** Distinct patients connected to a doctor through appointments.
- **Treatment cost:** Listed charge for a treatment, whether or not it was paid.
- **Collected revenue:** Sum of `payments.amount_paid`; this is not the same as charges.
- **Outstanding treatment:** A treatment without a paid payment record.

## Entity relationships

- A department has many doctors.
- A doctor has many appointments.
- A patient may have many appointments or none.
- An appointment may have many treatments or none.
- A treatment has a payment record in the generated dataset, but analytics tolerate a missing payment.

## Status values

- Appointment: `Completed`, `Scheduled`, `Cancelled`, `No-show`.
- Payment: `Paid`, `Pending`, `Partially Paid`.

