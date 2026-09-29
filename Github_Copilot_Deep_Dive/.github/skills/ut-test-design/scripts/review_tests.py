#!/usr/bin/env python3
"""Review an LDM test-design CSV and write machine-readable findings as JSON."""

from __future__ import annotations

import argparse
import csv
import json
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
ID_PATTERN = re.compile(r"LDM_TC_(\d{3})$")
OUTPUT_PATTERN = re.compile(
    r"status=([^;]+);\s*requestMitigation=(true|false);\s*"
    r"requestedSide=([^;]+);\s*reason=([^;]+)"
)
INPUT_PATTERN = re.compile(r"([^;=]+)=([^;]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("ldm-test-review-findings.json"),
    )
    return parser.parse_args()


def parse_input(value: str) -> dict[str, str]:
    return {key.strip(): raw.strip() for key, raw in INPUT_PATTERN.findall(value)}


def add_finding(
    findings: list[dict[str, object]],
    row_number: int,
    row: dict[str, str],
    rule_id: str,
    severity: str,
    message: str,
    fixable: bool,
    replacement: str = "",
) -> None:
    findings.append(
        {
            "row": row_number,
            "test_id": row.get("Test ID", ""),
            "rule_id": rule_id,
            "severity": severity,
            "message": message,
            "fixable": fixable,
            "replacement": replacement,
        }
    )


def expected_replacement(row: dict[str, str]) -> str:
    expected = row.get("expected output", "").strip()
    match = re.match(r"status=([^;]+);\s*requestMitigation=(true|false);\s*reason=([^;]+)", expected)
    if not match:
        return ""
    status, request, reason = match.groups()
    inputs = parse_input(row.get("clear input", ""))
    side = "NONE"
    if request == "true":
        side = inputs.get("risk", "UNKNOWN")
    return f"status={status}; requestMitigation={request}; requestedSide={side}; reason={reason}"


def review(csv_path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != EXPECTED_COLUMNS:
                add_finding(
                    findings,
                    1,
                    {},
                    "CSV_HEADER",
                    "error",
                    "CSV header does not match the required nine columns.",
                    False,
                )
            rows = list(reader)
    except (OSError, csv.Error) as error:
        raise RuntimeError(f"cannot read CSV: {error}") from error

    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        test_id = row.get("Test ID", "")
        if test_id in seen_ids:
            add_finding(findings, row_number, row, "DUPLICATE_ID", "error", "Test ID is duplicated.", False)
        seen_ids.add(test_id)
        if not ID_PATTERN.fullmatch(test_id):
            add_finding(findings, row_number, row, "INVALID_ID", "error", "Test ID must match LDM_TC_NNN.", False)
        if row.get("automated(yes/no)") not in {"yes", "no"}:
            add_finding(findings, row_number, row, "AUTOMATION_FLAG", "error", "automated(yes/no) must be yes or no.", True, "yes")
        if not row.get("test description", "").strip():
            add_finding(findings, row_number, row, "MISSING_DESCRIPTION", "error", "Test description is empty.", False)
        if not row.get("clear input", "").strip():
            add_finding(findings, row_number, row, "MISSING_INPUT", "error", "Clear input is empty.", False)
        if not row.get("expected output", "").strip():
            add_finding(findings, row_number, row, "MISSING_EXPECTED_OUTPUT", "error", "Expected output is empty.", False)
            continue

        expected = row["expected output"].strip()
        if "requestMitigation=" not in expected or "reason=" not in expected:
            add_finding(findings, row_number, row, "INCOMPLETE_EXPECTED_OUTPUT", "error", "Expected output must include requestMitigation and reason.", False)
        if "requestedSide=" not in expected:
            replacement = expected_replacement(row)
            add_finding(
                findings,
                row_number,
                row,
                "MISSING_REQUESTED_SIDE",
                "warning",
                "Expected output does not state requestedSide.",
                bool(replacement),
                replacement,
            )
        if row.get("actual output", "") != "":
            add_finding(findings, row_number, row, "DESIGN_TIME_ACTUAL_OUTPUT", "warning", "Design-time actual output should be blank.", True, "")
        if row.get("testcase type") == "Immutability" and "unchanged" not in row.get("expected output", "").lower() and "immutability" not in row.get("comments", "").lower():
            add_finding(findings, row_number, row, "IMMUTABILITY_ASSERTION", "warning", "Immutability case should state that input fields remain unchanged.", False)
        if row.get("testcase type") == "Determinism" and "same" not in row.get("test description", "").lower() and "repeat" not in row.get("comments", "").lower():
            add_finding(findings, row_number, row, "DETERMINISM_ASSERTION", "warning", "Determinism case should describe repeated identical evaluation.", False)

    return findings


def main() -> int:
    args = parse_args()
    try:
        findings = review(args.csv_path)
        args.output.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Review complete: {len(findings)} finding(s) written to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
