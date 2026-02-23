from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .models import ReminderRule


@dataclass(frozen=True)
class AppConfig:
    workbook_path: str
    tenants_sheet: str
    ledger_sheet: str
    reminder_rules: List[ReminderRule]


def load_config(path: str) -> AppConfig:
    config_path = Path(path)

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    
    
    rules = []
    for r in raw["reminder_rules"]:
        rule = ReminderRule(
            min_days=r["min_days"],
            max_days=r.get("max_days"),
            subject_template=r["subject_template"],
            body_template=r["body_template"],
        )
        rules.append(rule)


    return AppConfig(
        workbook_path=raw["workbook_path"],
        tenants_sheet=raw["tenants_sheet"],
        ledger_sheet=raw["ledger_sheet"],
        reminder_rules=rules,
    )