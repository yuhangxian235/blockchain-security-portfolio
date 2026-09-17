# Dune KYT Dashboard — Assembly Guide

Three queries map to three panels on a monitoring-style dashboard.



| File                         | Metric                          | Panel type                    |
| ---------------------------- | ------------------------------- | ----------------------------- |
| `01_unlimited_approvals.sql` | daily unlimited-approval volume | time series / bar chart       |
| `02_phishing_drain.sql`      | candidate approve→drain alerts  | table (review list)           |
| `03_peel_chain.sql`          | high fan-out layering nodes     | table ranked by fan-out width |

## How to build (≈15 min)



1. Log into Dune → New Query.

2. Paste each file's SQL, run, confirm results load (adjust table/column names if Dune's

   Ethereum schema version differs; the event names `ERC20_evt_Approval` /

   `ERC20_evt_Transfer` and `traces` are standard).

3. Save each query.

4. New Dashboard → add the three queries as panels; set #1 to a bar/line chart.

5. Add text panels: title "KYT / AML monitoring lab", note data is Ethereum mainnet,

   and link back to the traced case in `case-tracing-report/`.

## Why this is job-relevant

It turns the R1–R5 rules from the report into a shared, live dashboard that an

analyst team can watch — the deliverable a KYT team actually operates.