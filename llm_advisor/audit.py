from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


class AuditTrail:
    def __init__(self, output_file: str = "audit_log.jsonl") -> None:
        self.output_file = Path(output_file)

    def record(self, payload: dict[str, Any]) -> str:
        audit_id = str(uuid.uuid4())
        line = {"audit_id": audit_id, **payload}
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with self.output_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=True) + "\n")
        return audit_id
