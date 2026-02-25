from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import List, Dict, Iterable, Optional
from dataclasses import dataclass
from calendar import monthrange

from .models import (
    Tenant,
    LedgerEntry,
    ArrearsSnapshotRow,
    ReminderRule,
    ReminderRecord,
)
from .render import pick_rule, render_reminder


@dataclass(frozen=True)
class ChargeSlice:
    charge_date: date
    amount: float


# -----------------------------
# FIFO AGING LOGIC
# -----------------------------

def _fifo_oldest_unpaid_charge_date(
    charges: Iterable[ChargeSlice],
    total_paid: float,
) -> Optional[date]:

    remaining_paid = float(total_paid)

    for ch in charges:
        if remaining_paid <= 0:
            return ch.charge_date

        if remaining_paid >= ch.amount:
            remaining_paid -= ch.amount
            continue

        return ch.charge_date

    return None


def _days_overdue_from_ledger(
    lease_entries: List[LedgerEntry],
    as_of: date,
) -> Optional[int]:

    entries = [e for e in lease_entries if e.entry_date <= as_of]

    charges = sorted(
        (ChargeSlice(e.entry_date, float(e.amount))
         for e in entries if e.entry_type == "charge"),
        key=lambda c: c.charge_date,
    )

    total_paid = sum(float(e.amount)
                     for e in entries if e.entry_type == "payment")

    if not charges:
        return None

    oldest_unpaid = _fifo_oldest_unpaid_charge_date(charges, total_paid)

    if oldest_unpaid is None:
        return None

    return (as_of - oldest_unpaid).days


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


# -----------------------------
# MOVE-OUT PRORATION LOGIC
# -----------------------------

def _days_in_month(d: date) -> int:
    return monthrange(d.year, d.month)[1]


def _has_proration_charge(entries: List[LedgerEntry], move_out_date: date) -> bool:
    return any(
        e.entry_type == "charge" and e.entry_date == move_out_date
        for e in entries
    )


def _make_proration_entry(tenant: Tenant) -> LedgerEntry:
    assert tenant.move_out_date is not None

    d = tenant.move_out_date
    dim = _days_in_month(d)
    daily_rate = float(tenant.monthly_rent) / dim
    days_stayed = d.day
    amount = round(daily_rate * days_stayed, 2)

    return LedgerEntry(
        lease_id=tenant.lease_id,
        entry_date=d,
        amount=amount,
        entry_type="charge",
    )


# -----------------------------
# SNAPSHOT
# -----------------------------

def build_arrears_snapshot(
    tenants: List[Tenant],
    ledger: List[LedgerEntry],
    as_of: date,
) -> List[ArrearsSnapshotRow]:

    ledger_by_lease: Dict[str, List[LedgerEntry]] = defaultdict(list)

    for entry in ledger:
        if entry.entry_date <= as_of:
            ledger_by_lease[entry.lease_id].append(entry)

    snapshot: List[ArrearsSnapshotRow] = []

    for tenant in tenants:
        base_entries = ledger_by_lease.get(tenant.lease_id, [])
        entries = list(base_entries)

        # Add proration charge if applicable
        if tenant.move_out_date is not None and tenant.move_out_date <= as_of:
            if not _has_proration_charge(entries, tenant.move_out_date):
                entries.append(_make_proration_entry(tenant))

        total_charges = sum(e.amount for e in entries if e.entry_type == "charge")
        total_payments = sum(e.amount for e in entries if e.entry_type == "payment")
        balance = total_charges - total_payments

        overdue_anchor_date: Optional[date] = None

        if balance > 0:
            if tenant.move_out_date is not None and tenant.move_out_date <= as_of:
                overdue_anchor_date = tenant.move_out_date
                days_overdue = (as_of - overdue_anchor_date).days
            else:
                days_overdue = _days_overdue_from_ledger(entries, as_of)

                if days_overdue is not None:
                    charges = sorted(
                        (ChargeSlice(e.entry_date, float(e.amount))
                         for e in entries if e.entry_type == "charge"),
                        key=lambda c: c.charge_date,
                    )
                    total_paid = sum(
                        float(e.amount) for e in entries if e.entry_type == "payment"
                    )
                    overdue_anchor_date = _fifo_oldest_unpaid_charge_date(
                        charges, total_paid
                    )
        else:
            days_overdue = None

        bucket = _bucketize(days_overdue)

        snapshot.append(
            ArrearsSnapshotRow(
                lease_id=tenant.lease_id,
                tenant_name=tenant.tenant_name,
                property_name=tenant.property_name,
                manager_name=tenant.manager_name,
                balance=round(balance, 2),
                unit=tenant.unit,
                days_overdue=days_overdue,
                bucket=bucket,
                overdue_anchor_date=overdue_anchor_date,
            )
        )

    snapshot.sort(
        key=lambda r: (
            r.balance,
            r.days_overdue if r.days_overdue is not None else -1,
        ),
        reverse=True,
    )

    return snapshot


# -----------------------------
# REMINDERS
# -----------------------------

def build_reminders(
    snapshot: List[ArrearsSnapshotRow],
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