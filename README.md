# Tenant Arrears Tracker — Python Financial Data Processing

A project demonstrating how structured Excel tenant and payment records can be validated, processed into arrears snapshots, and exported for operational reporting. The included workbook is example data; no production deployment is claimed.

## What the source implements

- Load tenant and ledger worksheets using pandas, with required-column and transaction-type checks.
- Allocate payments against older charges (FIFO) and calculate remaining balances.
- Group arrears by days overdue (1–7, 8–30, 31–60, and 60+).
- Produce CSV arrears snapshots, reminders, and a dated reporting-history file.
- Produce reminder-message **drafts** as local text. No messages are transmitted.
- Apply a basic move-out proration rule when a Move_Out_Date is supplied. This rule adds a prorated charge; it is not a fully audited rental billing or legal reconciliation system.
- Run the workflow from a command-line interface using an explicit configuration file.

See `src/arrears_engine/io.py`, `engine.py`, `app.py` and `export.py` for the implemented logic.

## Quick start (synthetic demonstration)

From a clone of this repository, using Python 3.10+:

```powershell
git clone https://github.com/Nicola934/tenant-arrears-tracker.git
cd tenant-arrears-tracker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m arrears_engine.cli validate --config data/config.example.json
python -m arrears_engine.cli run --config data/config.example.json --as-of 2026-11-01 --out-dir outputs
python -m arrears_engine.cli status --config data/config.example.json
```

The sample configuration points to `data/tenant_arrears_mock.xlsx`. Outputs are written to the requested directory. Generated snapshots and reminder text should be treated as demonstration artefacts, not customer accounts.

## Data definitions and assumptions

**Input:** `Tenants` and `Ledger` sheets in an Excel workbook. Each ledger row has a lease ID, date, amount, and entry type (`charge` or `payment`).

**Balance:** Total included charges minus total included payments, calculated at the selected `--as-of` date.

**FIFO ageing:** Payments are applied against the oldest eligible charge to determine the oldest remaining unpaid charge date. The ageing buckets reflect that calculation, rather than a predictive risk score.

**Move-out proration:** Optional `Move_Out_Date` triggers a simplified prorated charge in the implementation. It should be checked against actual billing terms before use outside a demonstration.

**Reports:** A current and dated arrears snapshot, reminders CSV, email dry-run text, and history CSV. These are calculated exports; an independently verified Excel dashboard is not part of this repository's documented execution path.

## Verification limitations

This repository is portfolio evidence of implemented financial processing and reporting logic. Do not treat it as certified accounting software, legally verified rent calculations, or a production-ready property-management service. The published snapshot of the project should be tested with synthetic records and independently calculated expected balances before operational use.

For the associated business problem and other project work, see the [Lionyx-E website](https://github.com/Nicola934/lionyx-e-site).
