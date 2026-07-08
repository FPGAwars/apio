"""JSON exporter for apio report structured data."""
from __future__ import annotations
from typing import Any, Dict
import json

def to_json(report: Dict[str, Any]) -> str:
    """Render the structured report dict to a stable, pretty JSON string."""
    return json.dumps(report, indent=2, sort_keys=True)
