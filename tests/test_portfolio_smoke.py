"""Synthetic smoke tests for the public arrears-processing portfolio.

Run with: PYTHONPATH=src python -m unittest discover -s tests -v
Uses only temporary generated data; no customer data or email service.
"""
import tempfile
import unittest
from datetime import date
from pathlib import Path

import pandas as pd

from arrears_engine.app import run_pipeline
from arrears_engine.config import AppConfig
from arrears_engine.engine import build_arrears_snapshot, build_reminders
from arrears_engine.models import LedgerEntry, ReminderRule, Tenant


def tenant(lease_id: str = "TEST-001") -> Tenant:
    return Tenant(
        lease_id=lease_id, tenant_name="Synthetic Tenant", monthly_rent=500.0,
        due_day=1, unit="Unit A", property_name="Test Property",
        manager_name="Test Manager", contact_email="tenant@example.com",
    )


class ArrearsPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.as_of = date(2026, 3, 1)
        self.rules = [ReminderRule(
            min_days=1, max_days=None,
            subject_template="Payment reminder for {tenant_name}",
            body_template="{balance} overdue by {days_overdue} days.",
        )]

    def test_fifo_partial_payment_and_reminder(self):
        ledger = [
            LedgerEntry("TEST-001", date(2026, 1, 1), 500.0, "charge"),
            LedgerEntry("TEST-001", date(2026, 2, 1), 500.0, "charge"),
            LedgerEntry("TEST-001", date(2026, 1, 15), 600.0, "payment"),
        ]
        snapshot = build_arrears_snapshot([tenant()], ledger, self.as_of)
        self.assertEqual(len(snapshot), 1)
        row = snapshot[0]
        self.assertEqual(row.balance, 400.0)
        self.assertEqual(row.days_overdue, 28)
        self.assertEqual(row.bucket, "D08_30")
        reminders = build_reminders(snapshot, self.rules)
        self.assertEqual(len(reminders), 1)
        self.assertIn("Synthetic Tenant", reminders[0].subject)

    def test_fully_paid_tenant_has_no_arrears(self):
        ledger = [
            LedgerEntry("TEST-001", date(2026, 1, 1), 500.0, "charge"),
            LedgerEntry("TEST-001", date(2026, 1, 15), 500.0, "payment"),
        ]
        row = build_arrears_snapshot([tenant()], ledger, self.as_of)[0]
        self.assertEqual(row.balance, 0.0)
        self.assertIsNone(row.days_overdue)
        self.assertEqual(row.bucket, "Current")
        self.assertEqual(build_reminders([row], self.rules), [])

    def test_excel_input_to_csv_pipeline_using_synthetic_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workbook = root / "example.xlsx"
            output = root / "reports"
            tenants = pd.DataFrame([{
                "Lease_ID": "TEST-001", "Tenant_Name": "Synthetic Tenant",
                "Monthly_Rent": 500.0, "Due_Day": 1, "Unit": "Unit A",
                "Contact_Email": "tenant@example.com",
                "Property_Name": "Test Property", "Manager_Name": "Test Manager",
            }])
            ledger = pd.DataFrame([
                {"Lease_ID": "TEST-001", "Entry_Date": date(2026, 1, 1),
                 "Amount": 500.0, "Entry_Type": "CHARGE"},
                {"Lease_ID": "TEST-001", "Entry_Date": date(2026, 2, 1),
                 "Amount": 500.0, "Entry_Type": "CHARGE"},
                {"Lease_ID": "TEST-001", "Entry_Date": date(2026, 1, 15),
                 "Amount": 600.0, "Entry_Type": "PAYMENT"},
            ])
            with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
                tenants.to_excel(writer, sheet_name="Tenants", index=False)
                ledger.to_excel(writer, sheet_name="Ledger", index=False)
            cfg = AppConfig(str(workbook), "Tenants", "Ledger", self.rules)
            run_pipeline(cfg, as_of=self.as_of, out_dir=str(output))
            snapshot = pd.read_csv(output / "arrears_snapshot_latest.csv")
            self.assertEqual(len(snapshot), 1)
            self.assertAlmostEqual(float(snapshot.loc[0, "balance"]), 400.0)
            self.assertEqual(snapshot.loc[0, "bucket"], "D08_30")
            self.assertTrue((output / "reminders_2026-03-01.csv").exists())
            history = pd.read_csv(output / "arrears_history.csv")
            self.assertAlmostEqual(float(history.loc[0, "total_arrears"]), 400.0)
            self.assertTrue((output / "email_dryrun_2026-03-01.txt").exists())


if __name__ == "__main__":
    unittest.main()
