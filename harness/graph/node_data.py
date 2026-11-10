"""Optional JSON payload on graph node tuples (column index 8 after stage)."""

from __future__ import annotations

import json
from typing import Any


def decode_node_data(row: list) -> dict[str, Any]:
    if len(row) <= 8:
        return {}
    raw = row[8]
    if not raw or not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def encode_node_data(data: dict[str, Any]) -> str:
    if not data:
        return ""
    return json.dumps(data, separators=(",", ":"))
