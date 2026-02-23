# Tenant Arrears Tracker + Reminder Engine

A structured rent arrears monitoring system that calculates tenant balances deterministically, categorizes aging risk, generates reminder queues, and feeds an auto-refreshing Excel operations dashboard.

---

## Overview

Property managers often track rent manually using spreadsheets, leading to inconsistent calculations, missed follow-ups, and limited visibility into aging risk.

This project provides a structured arrears engine that processes tenant and ledger data, computes balances reliably, classifies overdue accounts, and exports operational reports for decision-making.

---

## Key Features

- Deterministic arrears calculation logic  
- Aging bucket classification (Current, 1–7, 8–30, 31–60, 60+)  
- Automated reminder generation  
- Property-level risk segmentation  
- Manager workload visibility  
- Historical arrears trend tracking  
- CLI-based validation and execution  
- Auto-refresh Excel dashboard integration  

---

## Architecture

Excel (Data Entry + Dashboard)  
→ Python Engine (Validation + Computation)  
→ CSV Snapshot + History Exports  
→ Excel Ops Dashboard (Power Query Refresh)

The computation layer is isolated from the dashboard, ensuring consistent calculations and clean separation of concerns.

---

## Project Structure

```
tenant-arrears-tracker/
│
├── README.md
├── requirements.txt
├── data/
│   └── config.example.json
├── docs/
│   ├── dashboard_overview.png
│   ├── cli_run_example.png
│   └── cli_validate_example.png
├── outputs/   (generated at runtime)
└── src/
    └── arrears_engine/
        ├── models.py
        ├── config.py
        ├── io.py
        ├── engine.py
        ├── export.py
        ├── app.py
        └── cli.py
```
### Generate Mock Workbook (Optional)

To generate a sample Excel workbook with mock tenants and ledger entries:

```bash
python scripts/generate_mock_workbook.py


---

## Installation

Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Validate Inputs

```bash
python -m arrears_engine.cli validate --config data/config.example.json
```

Checks:
- Config file validity
- Workbook path
- Required sheets
- Required columns

---

### Run Pipeline

```bash
python -m arrears_engine.cli run --config data/config.example.json
```

Optional:

```bash
python -m arrears_engine.cli run --config data/config.example.json --as-of 2026-02-01
```

---

### View System Status

```bash
python -m arrears_engine.cli status --config data/config.example.json
```

---

## Outputs

Running the pipeline generates:

- `arrears_snapshot_latest.csv`
- `arrears_snapshot_YYYY-MM-DD.csv`
- `arrears_history.csv`
- `reminders_YYYY-MM-DD.csv`
- `email_dryrun_YYYY-MM-DD.txt`

The Excel dashboard reads:

- arrears_snapshot_latest.csv  
- arrears_history.csv  

and refreshes automatically via Power Query.

---

## Operational Impact

This system enables:

- Reduced manual reconciliation
- Consistent arrears calculations
- Faster follow-up prioritization
- Clear aging risk visibility
- Portfolio-level decision intelligence

---

## Technologies Used

- Python
- Pandas
- CLI architecture
- Excel Power Query
- PivotTables
- Structured data modeling
```
