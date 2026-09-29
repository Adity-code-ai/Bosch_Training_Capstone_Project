#!/usr/bin/env python3
"""Apply safe, machine-generated fixes from a findings CSV to an LDM test CSV."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

TEST_COLUMNS = [
    "Test ID",
    "testcase name",
    "test description",
    "clear input",
    "testcase type",
    "expected output",
    "actual output",
    "automated(yes/no)",
    "comments",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tests_csv", type=Path)
    parser.add_argument("findings_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument(
        "--backup",
        action="store_true",
        help="write a .bak copy of the input test CSV before applying fixes",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with args.tests_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != TEST_COLUMNS:
                raise ValueError("test CSV header does not match the required schema")
            rows = list(reader)

        with args.findings_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            findings = list(csv.DictReader(handle))

        if args.backup:
            shutil.copy2(args.tests_csv, args.tests_csv.with_suffix(args.tests_csv.suffix + ".bak"))

        by_row: dict[int, list[dict[str, str]]] = {}
        for finding in findings:
            if finding.get("status", "open").lower() not in {"open", ""}:
                continue
            if finding.get("fixable(yes/no)") != "yes":
                continue
            try:
                row_number = int(finding["row"])
            except (KeyError, ValueError):
                continue
            by_row.setdefault(row_number, []).append(finding)

        applied = 0
        unresolved = 0
        for row_number, row in enumerate(rows, start=2):
            for finding in by_row.get(row_number, []):
                rule_id = finding.get("rule id")
                replacement = finding.get("replacement", "")
                if rule_id == "MISSING_REQUESTED_SIDE" and replacement:
                    row["expected output"] = replacement
                    applied += 1
                elif rule_id == "AUTOMATION_FLAG":
                    row["automated(yes/no)"] = replacement or "yes"
                    applied += 1
                elif rule_id == "DESIGN_TIME_ACTUAL_OUTPUT":
                    row["actual output"] = ""
                    applied += 1
                else:
                    unresolved += 1

        with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=TEST_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, csv.Error, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"Fix complete: wrote {args.output_csv}; applied {applied} fix(es); "
        f"left {unresolved} non-applicable finding(s) unchanged."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
