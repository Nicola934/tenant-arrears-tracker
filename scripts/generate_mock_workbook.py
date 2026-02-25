from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


def ensure_data_dir() -> Path:
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def build_tenants() -> pd.DataFrame:
    tenants = [
        {
            "Lease_ID": "T001",
            "Tenant_Name": "Sipho Dlamini",
            "Unit": "A01",
            "Property_Name": "Block A",
            "Manager_Name": "Manager A",
            "Contact_Email": "tenant001@example.com",
            "Monthly_Rent": 4500,
            "Due_Day": 1,
            "Status": "ACTIVE",
            "Phone": "+27 795822412",
        },
        {
            "Lease_ID": "T002",
            "Tenant_Name": "Lerato Mokoena",
            "Unit": "A02",
            "Property_Name": "Block A",
            "Manager_Name": "Manager A",
            "Contact_Email": "tenant002@example.com",
            "Monthly_Rent": 6000,
            "Due_Day": 1,
            "Status": "ACTIVE",
            "Phone": "+27 713356886",
        },
        {
            "Lease_ID": "T003",
            "Tenant_Name": "Thabo Nkosi",
            "Unit": "B01",
            "Property_Name": "Block B",
            "Manager_Name": "Manager B",
            "Contact_Email": "tenant003@example.com",
            "Monthly_Rent": 5200,
            "Due_Day": 1,
            "Status": "ACTIVE",
            "Phone": "+27 728882111",
        },
    ]
    return pd.DataFrame(tenants)


def build_ledger(as_of: date) -> pd.DataFrame:
    
    rows: list[dict] = []

    def add_entry(entry_id: int, lease_id: str, entry_date: date, entry_type: str, amount: float, reference: str):
        rows.append(
            {
                "Entry_ID": f"E{entry_id:05d}",
                "Lease_ID": lease_id,
                "Entry_Date": entry_date,
                "Entry_Type": entry_type,  # CHARGE / PAYMENT (your loader lowercases)
                "Amount": float(amount),   # IMPORTANT: positive amounts for BOTH charge and payment
                "Reference": reference,
            }
        )

    entry_id = 1

    charge_dates = [
        date(as_of.year, max(1, as_of.month - 2), 1),
        date(as_of.year, max(1, as_of.month - 1), 1),
        date(as_of.year, as_of.month, 1),
    ]

    # Tenant rents for consistency
    rent_map = {"T001": 4500, "T002": 6000, "T003": 5200}

    for lease_id, rent in rent_map.items():
        for d in charge_dates:
            add_entry(
                entry_id,
                lease_id,
                d,
                "CHARGE",
                rent,
                f"RENT {d.strftime('%Y-%m')}",
            )
            entry_id += 1

    # Add some payments (positive amounts)
    # T001 pays everything
    add_entry(entry_id, "T001", charge_dates[0], "PAYMENT", 4500, "PAY")
    entry_id += 1
    add_entry(entry_id, "T001", charge_dates[1], "PAYMENT", 4500, "PAY")
    entry_id += 1
    add_entry(entry_id, "T001", charge_dates[2], "PAYMENT", 4500, "PAY")
    entry_id += 1

    # T002 pays partially (in arrears)
    add_entry(entry_id, "T002", charge_dates[0], "PAYMENT", 3000, "PARTIAL PAY")
    entry_id += 1

    # T003 pays nothing (in arrears)
    # no payments

    return pd.DataFrame(rows)


def main() -> None:
    data_dir = ensure_data_dir()
    out_path = data_dir / "tenant_arrears_mock.xlsx"

    as_of = date.today()
    tenants_df = build_tenants()
    ledger_df = build_ledger(as_of=as_of)

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        tenants_df.to_excel(writer, sheet_name="Tenants", index=False)
        ledger_df.to_excel(writer, sheet_name="Ledger", index=False)

    print(f"Mock workbook created: {out_path.resolve()}")
    print(f"Tenants: {len(tenants_df)} | Ledger entries: {len(ledger_df)}")


if __name__ == "__main__":
    main()
