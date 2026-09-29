#!/usr/bin/env python3
"""Validate the structure and coverage of an LDM unit-test design CSV."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

EXPECTED_COLUMNS = [
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
ALLOWED_TYPES = {
    "Positive",
    "Negative",
    "Edge",
    "Boundary",
    "Priority",
    "Invalid Input",
    "Stale Input",
    "Determinism",
    "Immutability",
}
ID_PATTERN = re.compile(r"LDM_TC_(\d{3})$")
REQUIRED_REASONS = {
    "MitigationAllowed",
    "LdmDisabled",
    "InputInvalid",
    "InputStale",
    "SpeedOutOfRange",
    "NoDepartureRisk",
    "MatchingTurnSignal",
    "DriverOverride",
    "Unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    return parser.parse_args()


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    try:
        with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != EXPECTED_COLUMNS:
                errors.append(
                    f"header must be exactly {EXPECTED_COLUMNS!r}; got {reader.fieldnames!r}"
                )
            rows = list(reader)
    except (OSError, csv.Error) as error:
        return fail([f"cannot read CSV: {error}"])

    if not rows:
        errors.append("CSV must contain at least one test case")

    ids: list[int] = []
    reasons: set[str] = set()
    types: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        test_id = row.get("Test ID", "")
        match = ID_PATTERN.fullmatch(test_id)
        if not match:
            errors.append(f"row {row_number}: invalid test ID {test_id!r}")
        else:
            ids.append(int(match.group(1)))

        testcase_type = row.get("testcase type", "")
        types.add(testcase_type)
        if testcase_type not in ALLOWED_TYPES:
            errors.append(f"row {row_number}: unsupported testcase type {testcase_type!r}")

        if row.get("automated(yes/no)") != "yes":
            errors.append(f"row {row_number}: automated(yes/no) must be yes")
        if row.get("actual output", "") != "":
            errors.append(f"row {row_number}: actual output must be blank for design-time tests")
        if not row.get("expected output", "").strip():
            errors.append(f"row {row_number}: expected output is empty")

        expected_output = row.get("expected output", "")
        reasons.update(
            reason
            for reason in REQUIRED_REASONS
            if f"reason={reason}" in expected_output
        )

    if len(ids) != len(set(ids)):
        errors.append("test IDs must be unique")
    if ids and ids != list(range(1, len(ids) + 1)):
        errors.append("test IDs must be sequential starting at LDM_TC_001")
    missing_reasons = REQUIRED_REASONS - reasons
    if missing_reasons:
        errors.append(f"missing expected reason-code coverage: {sorted(missing_reasons)}")

    if errors:
        return fail(errors)

    print(
        f"CSV validation passed: {len(rows)} rows, exact schema, sequential IDs, "
        f"allowed types={sorted(types)}, reason coverage complete."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
