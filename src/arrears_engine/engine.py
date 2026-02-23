from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import List, Dict

from .models import(
    Tenant,
    LedgerEntry,
    ArrearsSnapshotRow,
    ReminderRule,
    ReminderRecord
)
from .render import pick_rule, render_reminder


def _bucketize(days_overdue: int | None) -> str:
    if days_overdue is None or days_overdue <= 0:
        return "Current"
    if 1 <= days_overdue <= 7:
        return "D01_07"
    if 8 <= days_overdue <= 30:
        return "D08_30"
    if 31 <= days_overdue <= 60:
        return "D31_60"
    return "D60_PLUS"


def build_arrears_snapshot(
        tenants: List[Tenant],
        ledger: List[LedgerEntry],
        as_of: date,
) -> List[ArrearsSnapshotRow]:
    
    #Group ledger entries by lease_id
    
    ledger_by_lease: Dict[str, List[LedgerEntry]] = defaultdict(list) # defaultdict(list) is 
    for entry in ledger:
        if entry.entry_date <= as_of:
            ledger_by_lease[entry.lease_id].append(entry)
    
    snapshot: List[ArrearsSnapshotRow] = []

    for tenant in tenants:
        entries = ledger_by_lease.get(tenant.lease_id, [])

        total_charges = sum(e.amount for e in entries if e.entry_type == "charge"
        )

        total_payments = sum(
            e.amount for e in entries if e.entry_type == "payment"
        )

        balance = total_charges - total_payments

        if balance > 0:
            charge_dates = [
                e.entry_date for e in entries if e.entry_type == "charge"
            ]

            if charge_dates:
                latest_charge = max(charge_dates)
                days_overdue = (as_of - latest_charge).days
            else:
                days_overdue = None
        else:
            days_overdue = None

        bucket = _bucketize(days_overdue)


        snapshot.append(
            ArrearsSnapshotRow(
                lease_id=tenant.lease_id,
                tenant_name=tenant.tenant_name,
                balance=round(balance, 2),
                days_overdue=days_overdue,
                bucket=bucket,
                property_name=tenant.property_name,
                manager_name=tenant.manager_name,
                unit=tenant.unit,
            )
        )
    snapshot.sort(key=lambda r: (
        r.balance,
        r.days_overdue if r.days_overdue is not None else -1,
    ),
    reverse=True,
    )
    return snapshot

def build_reminders(
        snapshot:List[ArrearsSnapshotRow],
        rules: List[ReminderRule],
) -> List[ReminderRecord]:
    reminders: List[ReminderRecord] = []

    for row in snapshot:
        if row.days_overdue is None:
            continue

        if row.balance <= 0:
            continue

        rule = pick_rule(rules, row.days_overdue)
        if rule is None:
            continue

        subject, body = render_reminder(rule, row)

        reminders.append(
            ReminderRecord(
                lease_id=row.lease_id,
                tenant_name=row.tenant_name,
                balance=row.balance,
                days_overdue=row.days_overdue,
                subject=subject,
                body=body,
            )
        )
    return reminders