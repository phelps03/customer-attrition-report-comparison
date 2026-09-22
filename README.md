# Customer Attrition Dashboard (report-backed)

Static, mobile-friendly customer retention dashboard built only from the FieldRoutes "All Time Customer List" customer report export. No FieldRoutes API pulls are required to refresh it.

Live: https://phelps03.github.io/customer-attrition-report-comparison/

## Data rules
- Source: FieldRoutes saved report "All Time Customer List" (Customers > Customer Reports > Saved Reports), CSV export.
- Eligibility: customers present in the report's "Has Completed Initial Service" population.
- One row per Customer ID. Cohort date is the earliest Initial Service across all report rows for that customer.
- Status: the report's Customer Status snapshot (Active / Frozen).
- The report's columns are Customer ID, Last Name, First Name, Customer Status, Initial Service, Subscription. It has no cancellation date, office, customer type, or sale source, so those views are intentionally absent.
- The public `data.json` contains only aggregated counts. No customer IDs, names, contact details, subscription labels, or credentials are published.

## Refresh (no API)
1. Export a fresh "All Time Customer List" CSV from FieldRoutes and keep it private.
2. In a trusted environment (never in this repo), run:
   `python3 build_data.py path/to/export.csv data.json --generated-at <export timestamp, ISO 8601>`
3. Publish the new `data.json` here. The script prints reconciliation counts (rows, unique customers, active/frozen) to check against the report before publishing.
