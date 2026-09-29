#!/usr/bin/env python3
"""Validate LDM CSV expected outputs against the documented decision ladder."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

INPUT_PATTERN = re.compile(r"([^;=]+)=([^;]+)")
OUTPUT_PATTERN = re.compile(
    r"status=([^;]+);\s*requestMitigation=(true|false);\s*"
    r"requestedSide=([^;]+);\s*reason=([^;]+)"
)


@dataclass(frozen=True)
class Decision:
    status: str
    request_mitigation: bool
    requested_side: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    return parser.parse_args()


def parse_input(value: str) -> dict[str, str]:
    return {key.strip(): raw_value.strip() for key, raw_value in INPUT_PATTERN.findall(value)}


def boolean(inputs: dict[str, str], key: str) -> bool:
    value = inputs.get(key)
    if value not in {"true", "false"}:
        raise ValueError(f"{key} must be true or false")
    return value == "true"


def evaluate(inputs: dict[str, str]) -> Decision:
    if not boolean(inputs, "inputValid"):
        return Decision("InputUnavailable", False, "NONE", "InputInvalid")
    if not boolean(inputs, "inputFresh"):
        return Decision("Degraded", False, "NONE", "InputStale")
    if not boolean(inputs, "enabled"):
        return Decision("MitigationInhibited", False, "NONE", "LdmDisabled")
    if not boolean(inputs, "speedInTrainingRange"):
        return Decision("MitigationInhibited", False, "NONE", "SpeedOutOfRange")

    risk = inputs.get("risk")
    if risk == "NONE":
        return Decision("MitigationInhibited", False, "NONE", "NoDepartureRisk")
    if risk == "LEFT" and boolean(inputs, "leftTurnSignalOn"):
        return Decision("MitigationInhibited", False, "NONE", "MatchingTurnSignal")
    if risk == "RIGHT" and boolean(inputs, "rightTurnSignalOn"):
        return Decision("MitigationInhibited", False, "NONE", "MatchingTurnSignal")
    if boolean(inputs, "driverOverride"):
        return Decision("MitigationInhibited", False, "NONE", "DriverOverride")
    if risk in {"LEFT", "RIGHT"}:
        return Decision("MitigationAllowed", True, risk, "MitigationAllowed")
    return Decision("MitigationInhibited", False, "NONE", "Unknown")


def parse_expected(value: str) -> Decision | None:
    match = OUTPUT_PATTERN.fullmatch(value.strip())
    if not match:
        return None
    return Decision(
        status=match.group(1),
        request_mitigation=match.group(2) == "true",
        requested_side=match.group(3),
        reason=match.group(4),
    )


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, csv.Error) as error:
        print(f"ERROR: cannot read CSV: {error}", file=sys.stderr)
        return 1

    for row_number, row in enumerate(rows, start=2):
        clear_input = row.get("clear input", "")
        expected_text = row.get("expected output", "")
        if clear_input.startswith("Call 1:"):
            continue
        try:
            inputs = parse_input(clear_input)
            actual = evaluate(inputs)
            expected = parse_expected(expected_text)
            if expected is None:
                errors.append(f"row {row_number}: expected output is not a single decision record")
            elif actual != expected:
                errors.append(
                    f"row {row_number} ({row.get('Test ID')}): expected {expected}, computed {actual}"
                )
        except ValueError as error:
            errors.append(f"row {row_number} ({row.get('Test ID')}): {error}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"LDM decision validation passed: {len(rows)} CSV rows checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
