---
name: ut-test-design
description: 'Design traceable, automation-ready CSV unit tests for ASW Lane Departure Mitigation decision logic. Use when creating or reviewing LDM component tests, decision-branch coverage, boundary tests, invalid or stale input tests, inhibit-reason priority tests, determinism tests, or input-immutability tests.'
argument-hint: 'Describe the LDM function, inputs, decision rules, reason-code priorities, or coverage goals for the test design.'
---

# LDM Unit-Test Design

## Purpose

Create a complete, traceable, automation-ready test design for the ASW Lane Departure Mitigation (LDM) decision logic in C++. The output is a CSV file suitable for Excel or a CSV-based test-management system.

## When to Use

Use this skill when the user asks to:

- Design or review unit tests for LDM decision logic
- Cover LDM decision branches or acceptance criteria
- Generate boundary, invalid-input, stale-input, or priority tests
- Verify mitigation-request behavior and reason codes
- Check deterministic behavior or input immutability

## Procedure

1. Inspect the workspace before designing tests. Read the LDM requirements, software design, decision-function interface, enums, constants, decision tables, existing tests, and reason-code definitions when available.
2. Identify the decision inputs, valid ranges, freshness rules, output fields, and inhibit-reason priority order from the workspace. Do not invent behavior that is not documented; record unresolved assumptions in the `comments` column.
3. Build a traceability checklist from the documented acceptance criteria and decision branches.
4. Create a minimal valid positive baseline in which LDM is enabled, inputs are valid and fresh, speed is within the configured range, risk is actionable, no matching turn signal inhibits the request, and driver override is inactive.
5. Vary one controlling condition at a time to cover positive and negative behavior. Include LDM enabled/disabled, risk `NONE`/`LEFT`/`RIGHT`, matching and non-matching turn signals, driver override active/inactive, valid/invalid inputs, and fresh/stale inputs.
6. Add boundary cases for the minimum and maximum valid speeds, immediately outside each boundary, and any documented timestamp or validity boundary.
7. Add priority cases where multiple inhibit conditions are active. Verify that the documented first applicable condition determines the reason code and that mitigation is inhibited.
8. Add determinism tests that execute the same snapshot repeatedly and compare outputs. Add immutability tests that compare the input snapshot before and after execution.
9. Assign sequential IDs in the format `LDM_TC_001`, `LDM_TC_002`, and so on. Use only the allowed testcase types listed below.
10. Write the CSV with the exact required header, quote fields containing commas, quotes, or line breaks, and escape embedded double quotes by doubling them.
11. Validate that every acceptance criterion, decision branch, reason-code branch, boundary, invalid-input case, stale-input case, priority case, determinism case, and immutability case is represented.
12. Save the completed file to `docs/ut-test-design/ldm-ut-test-design.csv` and confirm that it is valid CSV. Leave `actual output` blank because this is a design-time artifact unless an actual value is explicitly known.
13. Run [validate_csv.py](./scripts/validate_csv.py) to check the exact header, CSV parsing, field completeness, sequential IDs, allowed testcase types, blank actual outputs, and reason-code coverage.
14. Run [test_validation.py](./scripts/test_validation.py) to recompute each single-snapshot expected decision using the documented priority ladder and report mismatches.
15. Run [review_tests.py](./scripts/review_tests.py) to inspect the design for duplicate or invalid IDs, incomplete expected outputs, missing inputs or descriptions, invalid automation flags, non-blank design-time actual outputs, and weak determinism or immutability assertions.
16. Run [generate_findings_csv.py](./scripts/generate_findings_csv.py) to convert the review JSON into an Excel-ready findings report.
17. Run [fix_review_findings.py](./scripts/fix_review_findings.py) to apply only safe, explicitly marked fixes to a separate output CSV. Review non-fixable findings manually.

## LDM Decision Context

The function evaluates one input snapshot and determines whether a mitigation request is issued. Consider these factors:

- LDM enabled or disabled
- Risk: `NONE`, `LEFT`, or `RIGHT`
- Vehicle speed within the configured training operating range
- Left and right turn-signal status
- Driver override state
- Input validity
- Input freshness
- Reason-code priority when multiple inhibit conditions apply

## Required CSV Format

Use exactly this header and column order:

`Test ID,testcase name,test description,clear input,testcase type,expected output,actual output,automated(yes/no),comments`

Every expected output must state whether mitigation is requested and the expected reason code. Keep inputs explicit and realistic enough for direct automation.

Allowed testcase types:

- `Positive`
- `Negative`
- `Edge`
- `Boundary`
- `Priority`
- `Invalid Input`
- `Stale Input`
- `Determinism`
- `Immutability`

## Quality Checks

Before finishing, verify that:

- The CSV header exactly matches the required header.
- Each test ID is unique and sequential.
- Every row has the same number of fields as the header.
- Fields containing commas, quotes, or line breaks are correctly quoted.
- `actual output` is blank for design-time cases.
- Both mitigation-allowed and mitigation-inhibited outcomes are covered.
- All documented reason-code branches and priority ordering are covered.
- Assumptions and unavailable specifications are stated in `comments`.
- Transport, networking, AWS, and unrelated integration behavior is excluded.

## Validation Commands

Run these commands from the repository root after generating the CSV:

```powershell
python .github/skills/ut-test-design/scripts/validate_csv.py docs/ut-test-design/ldm-ut-test-design.csv
python .github/skills/ut-test-design/scripts/test_validation.py docs/ut-test-design/ldm-ut-test-design.csv
python .github/skills/ut-test-design/scripts/review_tests.py docs/ut-test-design/ldm-ut-test-design.csv -o docs/ut-test-design/ldm-test-review-findings.json
python .github/skills/ut-test-design/scripts/generate_findings_csv.py docs/ut-test-design/ldm-test-review-findings.json docs/ut-test-design/ldm-test-review-findings.csv
python .github/skills/ut-test-design/scripts/fix_review_findings.py docs/ut-test-design/ldm-ut-test-design.csv docs/ut-test-design/ldm-test-review-findings.csv docs/ut-test-design/ldm-ut-test-design-fixed.csv
```

The decision validator skips multi-call determinism rows whose input describes more than one snapshot. Those rows still require manual or C++ test execution to verify state isolation.
The fix script never overwrites the source CSV unless the user explicitly chooses to replace it; its normal output is `ldm-ut-test-design-fixed.csv`.

## Output

Save the artifact at:

`docs/ut-test-design/ldm-ut-test-design.csv`

After saving and validating it, respond only with a brief confirmation that the CSV file was created. Do not reproduce the CSV content in the response.
