from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

IDENTIFIER_RE = re.compile(r"^PP-IG-(\d{4})-(\d{6})$")


@dataclass
class IdentifierStore:
    db_path: Path

    def ensure(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS sequences "
                "(year INTEGER PRIMARY KEY, next_sequence INTEGER NOT NULL)"
            )
            conn.commit()

    def allocate(self, prefix: str, platform_code: str, year: int | None = None) -> str:
        year = year or datetime.now(UTC).year
        self.ensure()
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT next_sequence FROM sequences WHERE year = ?", (year,)
            ).fetchone()
            seq = 1 if row is None else int(row[0])
            conn.execute(
                "INSERT INTO sequences(year, next_sequence) VALUES(?, ?) "
                "ON CONFLICT(year) DO UPDATE SET next_sequence = excluded.next_sequence + 1",
                (year, seq),
            )
            conn.commit()
        return f"{prefix}-{platform_code}-{year}-{seq:06d}"


def validate_identifier(identifier: str) -> bool:
    return bool(IDENTIFIER_RE.match(identifier))
