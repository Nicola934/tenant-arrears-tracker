from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from .models import ArrearsSnapshotRow, ReminderRecord
from .utils import ensure_dir, rows_to_dicts, today_iso



def export_snapshot_csv(rows: list[ArrearsSnapshotRow], out_dir: str, as_of: date) -> tuple[Path, Path]:
    out_path = ensure_dir(out_dir) / f"arrears_{today_iso(as_of)}.csv"
    df = pd.DataFrame(rows_to_dicts(rows))
    df.to_csv(out_path, index=False)

    latest_path = ensure_dir(out_dir) / "arrears_snapshot_latest.csv"
    df.to_csv(latest_path, index=False)

    return latest_path, out_path

def export_reminders_csv(rows: list[ReminderRecord], out_dir: str, as_of: date) -> Path:
    out_path = ensure_dir(out_dir) / f"reminders_{today_iso(as_of)}.csv"
    df = pd.DataFrame(rows_to_dicts(rows))
    df.to_csv(out_path, index=False)
    return out_path

def export_email_dryrun(rows: list[ReminderRecord], out_dir: str, as_of: date) -> Path:
    out_path = ensure_dir(out_dir) / f"email_dryrun_{today_iso(as_of)}.txt"

    lines: list[str] = []
    for r in rows:
        lines.append(f"LEASE: {r.lease_id}")
        lines.append(f"TENANT: {r.tenant_name}")
        lines.append(f"DAYS OVERDUE: {r.days_overdue}")
        lines.append(f"BALANCE: {r.balance}")
        lines.append(f"SUBJECT: {r.subject}")
        lines.append("BODY:")
        lines.append(r.body)
        lines.append("-" * 40)

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path

def export_history_row(snapshot: list[ArrearsSnapshotRow], out_dir: str, as_of: date) -> Path:
    out_path = ensure_dir(out_dir) / "arrears_history.csv"

    total_arrears = sum(r.balance for r in snapshot if r.balance > 0)
    active_leases = sum(1 for r in snapshot if r.balance > 0)

    bucket_totals: dict[str, float] = {}
    for r in snapshot:
        bucket_totals[r.bucket] = bucket_totals.get(r.bucket, 0.0) + float(r.balance)

    average_arrears = total_arrears / active_leases if active_leases > 0 else 0.0
    if bucket_totals:
        highest_bucket = max(bucket_totals.items(), key=lambda x: x[1])[0]
    else:
        highest_bucket = "N/A"

    row = {
        "as_of_date": as_of.isoformat(),
        "total_arrears": round(total_arrears, 2),
        "active_leases": active_leases,
        "highest_bucket": highest_bucket,
        "average_arrears": round(average_arrears, 2),
    }

    df_new = pd.DataFrame([row])

    if out_path.exists():
        df_existing = pd.read_csv(out_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined["as_of_date"] = pd.to_datetime(
        df_combined["as_of_date"], errors="coerce"
    )

    df_combined = df_combined.sort_values("as_of_date").reset_index(drop=True)

    df_combined["as_of_date"] = pd.to_datetime(
        df_combined["as_of_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d").astype(str)

    df_combined.to_csv(out_path, index=False)
    return out_path
