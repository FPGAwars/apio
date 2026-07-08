"""Markdown exporter for apio report structured data."""
from __future__ import annotations
from typing import Any, Dict

def _utilization_table(report: Dict[str, Any]) -> str:
    util = report.get("utilization", {})
    lines = [
        "# FPGA Resource Utilization",
        "",
        "| Resource | Used | Total | Utilization |",
        "|---|---:|---:|---:|",
    ]
    for res, vals in util.items():
        used = int(vals.get("used", 0))
        total = int(vals.get("available", 0))
        pct = f"{int(100 * used / total)}%" if total else ""
        used_str = f"{used}" if used else ""
        total_str = f"{total}" if total else ""
        lines.append(f"| {res} | {used_str} | {total_str} | {pct} |")
    return "\n".join(lines)


def _clocks_table(report: Dict[str, Any]) -> str:
    clocks = report.get("fmax", {})
    if not clocks:
        return "\n_No clocks were found in the design._\n"
    lines = [
        "",
        "## Clock Information",
        "",
        "| Clock | Max Speed (MHz) |",
        "|---|---:|",
    ]
    for net, vals in clocks.items():
        name = net.split("$")[-1].rstrip("_")
        mhz = vals.get("achieved", 0.0)
        lines.append(f"| {name} | {mhz:.2f} |")
    return "\n".join(lines)


def to_markdown(report: Dict[str, Any]) -> str:
    """Render report dict to Markdown with utilization and clocks tables."""
    return _utilization_table(report) + "\n" + _clocks_table(report) + "\n"
