from arrears_engine.config import load_config
from arrears_engine.io import load_tenants, load_ledger
from datetime import date
from arrears_engine.engine import build_arrears_snapshot
from arrears_engine.engine import build_reminders

cfg = load_config("data/config.example.json")

tenants = load_tenants(cfg.workbook_path, cfg.tenants_sheet)
ledger = load_ledger(cfg.workbook_path, cfg.ledger_sheet)

print("Tenants loaded:", len(tenants))
print("Ledger entries loaded:", len(ledger))
print("First tenant:", tenants[0])
print("First ledger entry:", ledger[0])


snapshot = build_arrears_snapshot(
    tenants,
    ledger,
    as_of=date.today()
)

print("Snapshot rows:", len(snapshot))
print("First snapshot row:", snapshot[0])

reminders = build_reminders(snapshot, cfg.reminder_rules)
print("Reminders:", len(reminders))
if reminders:
    print("First reminder:", reminders[0])``