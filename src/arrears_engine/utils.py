from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Iterable, Any


def today_iso(d: date | None = None) -> str:
    d = d or date.today()
    return d.isoformat()


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def rows_to_dicts(rows: Iterable[Any]) -> list[dict]:
    # works for dataclasses like ArrearsSnapshotRow / ReminderRecord
    # asdict(dataclass_obj) converts it to a plain dict (perfect for DataFrame/CSV)
    return [asdict(r) for r in rows]