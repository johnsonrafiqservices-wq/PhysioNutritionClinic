# Billing / Invoicing App (User & Staff Guide)

This application handles **invoices**, **payments**, **receipts**, **insurance claims**, **payment plans**, **CSV exports**, **refunds**, **billing reports**, and **audit logging**.

> **Latest additions:** Aging chart on dashboard, payment method doughnut chart, billing reports page, CSV export for invoices & payments, payment refunds, overpayment warnings, advanced filtering on invoice & payment lists, and `BillingAuditLog` tracking every key financial action.



It is designed for clinic finance/front-desk staff to:

- Create invoices for patients
- Add services / items to invoices
- Track invoice status (draft/sent/paid/overdue/cancelled)
- Record payments (optionally linked to an invoice)
- Print professional invoice PDFs and payment receipts (with QR codes)
- Create and print insurance claims
- Create payment plans for invoices


## 1) Main Concepts (Data)

### Invoice
An `Invoice` represents a bill issued to a **single patient**.

Key fields:

- `invoice_number` (e.g. `INV-000001`)
- `patient`
- `issue_date` (auto)
- `due_date`
- `status`: `draft`, `sent`, `paid`, `overdue`, `cancelled`
- Totals: `subtotal`, `tax_rate`, `tax_amount`, `discount_amount`, `total_amount`

Important calculations:

- Invoice totals are computed from line items using `invoice.calculate_totals()`.
- `invoice.get_total_paid()` sums completed payments.
- `invoice.get_balance_due()` returns remaining balance.


### Invoice Line Item
An `InvoiceLineItem` is an item/service on an invoice.

Key fields:

- `invoice`
- `service` (optional)
- `description`
- `quantity`
- `unit_price`
- `total_amount`

Behavior:

- When a line item is saved, it updates its `total_amount` and triggers invoice total recalculation.


### Payment
A `Payment` represents money received from a patient.

Key fields:

- `payment_id` (e.g. `PAY-000001`)
- `patient`
- `invoice` (optional)
- `amount`
- `payment_method`: cash, credit_card, debit_card, check, bank_transfer, insurance
- `status`: pending, completed, failed, refunded
- `reference_number` (optional)
- `processed_by`

Behavior:

- When a completed payment is recorded against an invoice, the invoice can automatically become `paid` if total completed payments cover the invoice total.


## 2) Permissions / Access

Most billing pages require login, and in many places the project enforces billing/finance access (depending on configuration).

If a user cannot access billing pages:

- Confirm the user is logged in
- Confirm the user has the correct permission / role for billing/finance


## 3) Key Pages (URLs)

These are defined in `billing/urls.py`.

### Dashboard
- `/billing/` (name: `billing_dashboard`)

Shows high-level finance metrics like monthly revenue, outstanding amount, daily payments, etc.

### Invoices
- `/billing/invoices/` (list)
- `/billing/invoices/create/` (create invoice via form)
- `/billing/invoices/create-for-patient/` (quick draft invoice for selected patient)
- `/billing/invoices/<id>/` (detail)
- `/billing/invoices/<id>/edit/` (edit)
- `/billing/invoices/<id>/pdf/` (printable invoice)
- `/billing/invoices/<id>/status/` (status update)
- `/billing/invoices/aging-report/` (aging)

### Payments
- `/billing/payments/` (list)
- `/billing/payments/create/` (create payment)
- `/billing/invoices/<invoice_id>/payment/` (create payment for a specific invoice)
- `/billing/payments/<id>/` (detail)
- `/billing/payments/<id>/receipt/` (printable receipt)

### Insurance Claims
- `/billing/claims/` (list)
- `/billing/claims/create/` (create)
- `/billing/invoices/<invoice_id>/claim/` (create for invoice)
- `/billing/claims/<id>/print/` (print view)

### Payment Plans
- `/billing/payment-plans/` (list)
- `/billing/invoices/<invoice_id>/payment-plan/` (create plan)
- `/billing/payment-plans/<id>/` (detail)


## 4) Common Staff Workflows

### A) Create an invoice for a patient (standard)
1. Go to **Invoices**: `/billing/invoices/`
2. Click **Create Invoice**: `/billing/invoices/create/`
3. Select the patient
4. Set due date
5. Add line items (services/items)
6. Save
7. Review totals on the invoice
8. Optionally update the invoice status to **Sent**


### B) Create a draft invoice quickly for a selected patient
1. From the billing dashboard or invoice list, use the quick action that hits:
   `/billing/invoices/create-for-patient/`
2. The system generates an `INV-xxxxxx` number and creates a **Draft** invoice
3. You are redirected to edit the invoice to add services/items


### C) Print / share the invoice
1. Open the invoice detail page
2. Use the PDF/print action:
   `/billing/invoices/<id>/pdf/`

Notes:

- The invoice printout includes a **QR code** that links back to that invoice PDF URL.


### D) Record a payment against an invoice
1. Open the invoice detail page
2. Click **Record Payment** (usually links to):
   `/billing/invoices/<invoice_id>/payment/`
3. Enter payment amount and method
4. Set payment status (typically **completed**)
5. Save

Automatic behavior:

- If total completed payments are greater than or equal to the invoice total, the invoice status becomes `paid`.


### E) Print a receipt after payment
1. Open the payment detail page or after saving a payment
2. Open receipt:
   `/billing/payments/<payment_id>/receipt/`

Notes:

- The receipt printout includes a **QR code** that links back to the receipt URL.


### F) Record a payment not linked to an invoice
You can record general payments directly against a patient:

1. Go to `/billing/payments/create/`
2. Select the patient
3. Leave invoice blank
4. Enter payment details


## 5) Status Guidelines

### Invoice Status
- `draft`
  - Invoice is being prepared, not yet issued
- `sent`
  - Invoice has been issued to the patient
- `paid`
  - Fully paid (based on completed payments)
- `overdue`
  - Past due date and not fully paid
- `cancelled`
  - Cancelled / void

### Payment Status
- `pending`
  - Not finalized
- `completed`
  - Counts toward invoice payment totals
- `failed`
  - Not successful
- `refunded`
  - Payment reversed


## 6) Printing Notes (Invoice & Receipt)

- Invoice template: `templates/billing/invoice_pdf.html`
- Receipt template: `templates/billing/payment_receipt.html`

The print layouts are designed to be professional and consistent with other clinic printouts.

QR Codes:

- Generated in `billing/views.py` using the `qrcode` library
- Embedded into the templates as base64 PNG (`data:image/png;base64,...`)


## 7) Troubleshooting

### Invoice shows wrong totals
- Verify line items quantities/prices
- Saving a line item triggers `invoice.calculate_totals()`
- If totals still look wrong, re-save the invoice or line items to force recalculation

### Payment cannot be created / validation fails
- If no invoice is selected, a patient must be selected
- If an invoice is selected, payment amount cannot exceed balance due
- If invoice is already `paid`, the system warns and blocks additional payments

### Receipt or invoice print layout overlaps footer
- Ensure the print CSS has enough bottom padding
- Avoid adding long blocks at the end of the content without page-break handling


## 8) Developer Reference

- Routes: `billing/urls.py`
- Views: `billing/views.py`
- Models: `billing/models.py`
- Forms: `billing/forms.py`

Templates (common):

- `templates/billing/invoice_list.html`
- `templates/billing/invoice_detail.html`
- `templates/billing/invoice_create.html`
- `templates/billing/invoice_edit.html`
- `templates/billing/invoice_pdf.html`
- `templates/billing/payment_create.html`
- `templates/billing/payment_list.html`
- `templates/billing/payment_detail.html`
- `templates/billing/payment_receipt.html`
