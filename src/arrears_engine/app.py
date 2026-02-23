from __future__ import annotations

from datetime import date

from .config import AppConfig
from .io import load_tenants, load_ledger
from .engine import build_arrears_snapshot, build_reminders
from .export import export_snapshot_csv, export_email_dryrun, export_reminders_csv, export_history_row


def run_pipeline(cfg: AppConfig, as_of: date, out_dir: str = "outputs") -> dict[str, str]:
    tenants = load_tenants(cfg.workbook_path, cfg.tenants_sheet)
    ledger = load_ledger(cfg.workbook_path, cfg.ledger_sheet)

    snapshot = build_arrears_snapshot(tenants, ledger, as_of=as_of)
    reminders = build_reminders(snapshot, cfg.reminder_rules)

    
    snap_path = export_snapshot_csv(snapshot, out_dir=out_dir, as_of=as_of)
    rem_path = export_reminders_csv(reminders, out_dir=out_dir, as_of=as_of)
    dry_path = export_email_dryrun(reminders, out_dir=out_dir, as_of=as_of)
    hist_path = export_history_row(snapshot, out_dir=out_dir, as_of=as_of)

    return {
        "snapshot_csv": str(snap_path),
        "reminders_csv": str(rem_path),
        "email_dryrun": str(dry_path),
        "history_csv": str(hist_path)
    }