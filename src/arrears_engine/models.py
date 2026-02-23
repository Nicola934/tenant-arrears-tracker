from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass(frozen=True)
class Tenant:
    lease_id: str
    tenant_name: str
    monthly_rent: float
    due_day: int # e.g. 1 for 1st of month
    unit: str
    property_name: str
    manager_name: str
    contact_email: str
    
@dataclass(frozen=True)
class LedgerEntry:
    lease_id: str
    entry_date: date 
    amount: float
    entry_type: str # charge or payment

@dataclass(frozen=True)
class ReminderRule:
    min_days: int
    max_days: Optional[int]
    subject_template: str
    body_template: str

@dataclass(frozen=True)
class ArrearsSnapshotRow:
    lease_id: str
    tenant_name: str
    property_name: str
    manager_name: str
    balance: float
    unit: str
    days_overdue: Optional[int]
    bucket: str

@dataclass(frozen=True)
class ReminderRecord:
    lease_id: str
    tenant_name: str
    balance: float
    days_overdue: int
    balance: float
    subject: str
    body: str