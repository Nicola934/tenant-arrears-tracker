from __future__ import annotations

from .models import ReminderRule, ArrearsSnapshotRow

def pick_rule(rules: list[ReminderRule], days_overdue: int) -> ReminderRule | None:
    for rule in rules:
        if days_overdue < rule.min_days: # if days_overdue is greater than rule.min_days then
            continue # skips the current loop and moves to the next tenant or rule without sending a reminder.

        if rule.max_days is None:
            return rule
        
        if rule.min_days <= days_overdue <= rule.max_days:
            return rule
    return None

def render_reminder(rule: ReminderRule, row: ArrearsSnapshotRow) -> tuple[str, str]:
    subject = rule.subject_template.format(
        tenat_name=row.tenant_name,
        balance=row.balance,
        days_overdue=row.days_overdue,
        lease_id=row.lease_id,
        bucket=row.bucket,
    )

    body = rule.body_template.format(
        tenant_name=row.tenant_name,
        balance=row.balance,
        days_overdue=row.days_overdue,
        lease_id=row.lease_id,
        bucket=row.bucket,
    )

    return subject, body