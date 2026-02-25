# Tenant Arrears Tracker + Ops Dashboard

Production-grade Python automation system for property managers.
Automates arrears aging, FIFO payment allocation, reminder generation, and operational reporting from structured Excel inputs.

Designed for admin-heavy property operations where accuracy, repeatability, and auditability matter.

---

## 1. Domain Problem

Property managers deal with recurring rent charges, partial payments, move-outs, and inconsistent ledger records.
Manual arrears tracking leads to:

* Incorrect aging buckets
* Misapplied payments
* Inconsistent reminder timing
* No clear historical reporting
* High administrative overhead

This system solves that.

It processes tenant and ledger data from Excel, applies strict FIFO arrears logic, handles partial payments and move-out proration correctly, and produces:

* Arrears snapshot (CSV)
* Reminder list (CSV)
* Historical outputs for dashboard tracking

An Excel Ops Dashboard automatically updates from snapshot + history data.

---

## 2. Core Features

* Excel-based tenant + ledger ingestion
* FIFO arrears aging engine
* Accurate handling of partial payments
* Move-out proration support
* Config-driven reminder rules
* CLI-based execution (run, validate, status)
* Snapshot + reminders CSV export
* Excel Ops Dashboard integration
* Dry-run mode for safe testing
* Deterministic, auditable outputs

This is automation designed for production, not experimentation.

---

## 3. Architecture Overview

The system follows a clean layered structure:

CLI → Application Layer → Domain Engine → I/O Layer → Outputs

### Key Modules

models.py
Defines core domain objects:

* Tenant
* LedgerEntry
* ArrearsSnapshotRow
* ReminderRule
* ReminderRecord

These are structured representations of business entities.

---

io.py
Handles:

* Excel ingestion (tenants + ledger)
* Config loading
* CSV output writing

Strict separation of I/O from business logic ensures testability.

---

engine.py
Core arrears computation logic:

* FIFO charge allocation
* Payment application
* Aging bucket classification
* Move-out proration handling
* Snapshot generation

This is the deterministic engine.

---

render.py
Responsible for:

* Selecting applicable reminder rules
* Rendering reminder messages
* Formatting reminder outputs

Separates business logic from communication logic.

---

cli.py
Provides command-line interface:

* run
* validate-config
* status
* --dry-run

This turns the system into an operational tool rather than a script.

---

## 4. FIFO Arrears Logic (Why It Matters)

FIFO = First-In, First-Out.

Payments are applied to the oldest unpaid charges first.

Why this is critical:

* Prevents artificial aging distortion
* Ensures legal defensibility
* Produces correct “days overdue” calculations
* Reflects real-world accounting standards

Without FIFO:
A tenant paying partially could appear current on new charges while old balances remain hidden.

With FIFO:
The system identifies the true oldest unpaid charge and calculates arrears age accurately.

This is fundamental to reliable arrears reporting.

---

## 5. Partial Payments

Partial payments are correctly allocated across historical charges.

Example:

January charge: 5000
February charge: 5000
Payment: 6000

Allocation:

* January fully cleared (5000)
* February partially cleared (1000 unpaid = 4000 remaining)

The engine tracks residual balances and computes aging accordingly.

No approximations. No manual adjustments required.

---

## 6. Move-Out Proration

Tenants who vacate mid-month must not be charged full rent.

The engine supports:

* Move-out date recognition
* Prorated charge calculation
* Correct aging based on adjusted balances

This prevents inflated arrears figures and ensures financial fairness.

Critical for portfolio integrity and reporting accuracy.

---

## 7. Outputs

Each run produces:

outputs/

* arrears_snapshot_YYYY-MM-DD.csv
* reminders_YYYY-MM-DD.csv
* email_dryrun_YYYY-MM-DD.txt (if dry-run)

Snapshot contains:

* Tenant ID
* Total arrears
* Oldest unpaid charge date
* Days overdue
* Aging bucket (D01_07, D08_30, D31_60, D60_PLUS)

These files feed the Excel Ops Dashboard.

---

## 8. Ops Dashboard

The Excel Ops Dashboard:

* Reads latest snapshot + history
* Displays arrears bucket distribution
* Tracks trend over time
* Shows operational KPIs
* Supports management-level reporting

The Python system is the data engine.
The Excel dashboard is the presentation layer.

Separation of concerns improves maintainability.

---

## 9. Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/tenant-arrears-tracker.git
cd tenant-arrears-tracker
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 10. Project Structure

```
Sample1_Tenant_Arrears_Tracker/
│
├── requirements.txt
├── README.md
│
├── src/
│   └── arrears_engine/
│       ├── __init__.py
│       ├── models.py
│       ├── config.py
│       ├── utils.py
│       ├── io.py
│       ├── render.py
│       ├── engine.py
│       └── cli.py
│
├── scripts/
│   └── generate_mock_workbook.py
│
├── data/
│   ├── config.example.json
│   └── tenant_arrears_mock.xlsx
│
├── outputs/
│
└── docs/
    ├── Sample1_OnePager.pdf
    └── onepager_preview-1.png
```

---

## 11. CLI Usage

Run full pipeline:

```bash
python -m arrears_engine.cli run
```

Dry run (no final email send simulation):

```bash
python -m arrears_engine.cli run --dry-run
```

Validate configuration:

```bash
python -m arrears_engine.cli validate-config
```

Check system status:

```bash
python -m arrears_engine.cli status
```

This allows scheduling via:

* Windows Task Scheduler
* Cron jobs
* CI/CD pipelines
* Remote execution scripts

---

## 12. Reliability & Design Principles

* Deterministic outputs
* Separation of concerns
* No business logic in I/O layer
* Strict domain modeling
* Config-driven rules
* Safe dry-run mode
* Extensible architecture

Designed to scale from:
Small portfolio → Multi-property operations → Productized automation
<<<<<<< HEAD

---

## 13. Use Cases

* Property managers
* Student accommodation operators
* Rental portfolio administrators
* Finance ops teams
* Admin-heavy SMEs

---

## 14. Future Extensions

* Email API integration
* Database-backed ledger ingestion
* Web dashboard layer
* Multi-property segmentation
* Role-based reporting

The architecture supports growth without structural refactor.

---
=======

---

## 13. Use Cases

* Property managers
* Student accommodation operators
* Rental portfolio administrators
* Finance ops teams
* Admin-heavy SMEs

---

## 14. Future Extensions

* Email API integration
* Database-backed ledger ingestion
* Web dashboard layer
* Multi-property segmentation
* Role-based reporting

The architecture supports growth without structural refactor.

---


>>>>>>> d36f1a4 (feat: finalize tenant arrears tracker with proration and CLI improvements)
