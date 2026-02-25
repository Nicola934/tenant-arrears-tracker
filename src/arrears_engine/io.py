from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd

from .models import Tenant, LedgerEntry


def _require_columns(df: pd.DataFrame, required: List[str], context: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"{context}: missing required columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Lease_id": "Lease_ID",
        "LEASE_ID": "Lease_ID",
        "lease_id": "Lease_ID",
        "entry_date": "Entry_Date",
        "entry_type": "Entry_Type",
        "tenant_name": "Tenant_Name",
    }
    return df.rename(columns=rename_map)


def load_tenants(workbook_path: str, sheet: str) -> List[Tenant]:
    df = pd.read_excel(workbook_path, sheet_name=sheet)
    df = _normalize_columns(df)

    required = [
        "Lease_ID",
        "Tenant_Name",
        "Monthly_Rent",
        "Due_Day",
        "Unit",
        "Contact_Email",
        "Property_Name",
        "Manager_Name",
    ]
    _require_columns(df, required, context=f"Tenants sheet '{sheet}'")

    # Optional Move_Out_Date
    if "Move_Out_Date" in df.columns:
        df["Move_Out_Date"] = pd.to_datetime(df["Move_Out_Date"], errors="coerce")
    else:
        df["Move_Out_Date"] = pd.NaT

    tenants: List[Tenant] = []

    for _, row in df.iterrows():
        tenants.append(
            Tenant(
                lease_id=str(row["Lease_ID"]).strip(),
                tenant_name=str(row["Tenant_Name"]).strip(),
                monthly_rent=float(row["Monthly_Rent"]),
                due_day=int(row["Due_Day"]),
                unit=str(row["Unit"]).strip(),
                contact_email=str(row["Contact_Email"]).strip(),
                property_name=str(row["Property_Name"]).strip() if pd.notna(row["Property_Name"]) else "UNKNOWN",
                manager_name=str(row["Manager_Name"]).strip() if pd.notna(row["Manager_Name"]) else "UNKNOWN",
                move_out_date=row["Move_Out_Date"].date() if pd.notna(row["Move_Out_Date"]) else None,
            )
        )

    return tenants


def load_ledger(workbook_path: str, sheet: str) -> List[LedgerEntry]:
    df = pd.read_excel(workbook_path, sheet_name=sheet)
    df = _normalize_columns(df)

    required = ["Lease_ID", "Entry_Date", "Amount", "Entry_Type"]
    _require_columns(df, required, context=f"Ledger sheet '{sheet}'")

    df["Entry_Date"] = pd.to_datetime(df["Entry_Date"], errors="coerce")

    bad_dates = df["Entry_Date"].isna()
    if bad_dates.any():
        bad_rows = df[bad_dates].index.tolist()
        raise ValueError(f"Ledger sheet '{sheet}': invalid Entry_Date in rows {bad_rows}")

    entries: List[LedgerEntry] = []

    for _, row in df.iterrows():
        entry_type = str(row["Entry_Type"]).strip().lower()

        if entry_type not in {"charge", "payment"}:
            raise ValueError(
                f"Invalid Entry_Type '{row['Entry_Type']}'. Use 'charge' or 'payment'."
            )

        entries.append(
            LedgerEntry(
                lease_id=str(row["Lease_ID"]).strip(),
                entry_date=row["Entry_Date"].date(),
                amount=float(row["Amount"]),
                entry_type=entry_type,
            )
        )

    return entries