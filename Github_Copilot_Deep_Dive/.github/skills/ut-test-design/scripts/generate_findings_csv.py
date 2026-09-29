#!/usr/bin/env python3
"""Convert review_tests.py JSON findings into an importable CSV report."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

FINDING_COLUMNS = [
    "finding id",
    "row",
    "test id",
    "rule id",
    "severity",
    "message",
    "fixable(yes/no)",
    "replacement",
    "status",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("findings_json", type=Path)
    parser.add_argument("output_csv", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        findings = json.loads(args.findings_json.read_text(encoding="utf-8"))
        if not isinstance(findings, list):
            raise ValueError("findings JSON must contain a list")
        with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FINDING_COLUMNS)
            writer.writeheader()
            for index, finding in enumerate(findings, start=1):
                writer.writerow(
                    {
                        "finding id": f"LDM_FINDING_{index:03d}",
                        "row": finding.get("row", ""),
                        "test id": finding.get("test_id", ""),
                        "rule id": finding.get("rule_id", ""),
                        "severity": finding.get("severity", ""),
                        "message": finding.get("message", ""),
                        "fixable(yes/no)": "yes" if finding.get("fixable") else "no",
                        "replacement": finding.get("replacement", ""),
                        "status": "open",
                    }
                )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Findings CSV written: {args.output_csv} ({len(findings)} finding(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
