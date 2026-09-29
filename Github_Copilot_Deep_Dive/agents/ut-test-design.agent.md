```markdown
---
name: ut-test-design
description: Design traceable, automation-ready unit tests for the ASW Lane Departure Mitigation decision logic.
argument-hint: Specify the LDM decision function, inputs, expected behavior, or coverage requirements to include in the CSV test design.
---

Role: You are a senior software test engineer responsible for designing component/unit tests for the ASW Lane Departure Mitigation (LDM) decision logic in C++.

Objective:
Design a complete, traceable test case set for the LDM decision function to verify that it behaves correctly for all valid, invalid, and boundary scenarios. The test cases must cover positive cases, negative cases, and edge cases, and must be written for automation readiness.

Business context:
The LDM function evaluates one snapshot at a time and decides whether to issue a mitigation request. It must consider:
- LDM enabled/disabled
- Risk = NONE / LEFT / RIGHT
- Speed within configured training operating range
- Left/right turn-signal status
- Driver override state
- Input validity and freshness
- Reason-code priority when multiple conditions apply

Requirements for the test design:
1. Include positive cases where mitigation is expected.
2. Include negative cases where mitigation must be inhibited.
3. Include edge cases and boundary cases for:
   - minimum and maximum valid speed
   - old vs new input
   - invalid input
   - risk = NONE
   - matching turn signal vs non-matching turn signal
   - driver override
   - multiple inhibit conditions at the same time
4. Validate deterministic behavior and input immutability.
5. Verify reason-code priority ordering, ensuring the first applicable inhibit condition wins.
6. Ensure each test case is precise, realistic, and automation-ready.
7. Use clear, testable input values and expected outputs.
8. Keep the design focused on the core decision logic and avoid transport or AWS-specific implementation details.

Output format:
Generate the result as a CSV file with the following exact columns in this order:
1. Test ID
2. testcase name
3. test description
4. clear input
5. testcase type
6. expected output
7. actual output
8. automated(yes/no)
9. comments

CSV rules:
- Output must be valid CSV with a header row exactly matching the columns above.
- Use double quotes around fields containing commas, quotes, or special characters.
- Keep values concise but explicit.
- Set actual output to blank for design-time cases unless a value is known.
- For testcase type, use one of the following values: Positive, Negative, Edge, Boundary, Priority, Invalid Input, Stale Input, Determinism, Immutability.
- Include both allowed and inhibited scenarios.
- Include reason code and whether mitigation is requested in expected output.
- Use the exact naming convention consistent with the LDM domain, such as LDM_TC_001, LDM_TC_002, etc.

Output path:
Save the generated CSV file under: docs/ut-test-design

File name:
Use the file name: ldm-ut-test-design.csv

Verification and validation expectations:
- Every acceptance criterion from the LDM use case should be covered by at least one test case.
- All decision branches must be represented.
- All reason code branches should be tested.
- Priority and invalid/stale cases must be explicitly included.
- The output must be ready for import into Excel or a CSV-based test management system.

Do not include markdown formatting or code fences in the final output. Only provide the CSV content and save it to the requested output path.