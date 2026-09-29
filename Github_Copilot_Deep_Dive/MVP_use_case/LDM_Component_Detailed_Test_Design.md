# LDM Component Detailed Test Design

## 1. Purpose

This document provides the detailed Markdown representation of the test cases defined in `docs/ut-test-design/ldm-ut-test-design.csv`. Each test case contains the same nine fields as the CSV source of truth:

1. Test ID
2. Testcase name
3. Test description
4. Clear input
5. Testcase type
6. Expected output
7. Actual output
8. Automated (yes/no)
9. Comments

The test target is the pure `evaluateLdm(const LdmInput& input)` decision function. These are design-time test cases.

## 2. Decision Priority

The expected priority order is:

1. Invalid input
2. Stale input
3. LDM disabled
4. Speed out of range
5. No departure risk
6. Matching turn signal
7. Driver override
8. Mitigation allowed

## 3. Detailed Test Cases

### LDM_TC_001 - Valid_Left_Request

1. **Test ID:** `LDM_TC_001`
2. **Testcase name:** `Valid_Left_Request`
3. **Test description:** Enabled LDM with LEFT risk, valid inputs, no turn signal, and no driver override; mitigation should be permitted.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Positive`
6. **Expected output:** `status=MitigationAllowed; requestMitigation=true; requestedSide=LEFT; reason=MitigationAllowed`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Baseline positive path.

### LDM_TC_002 - Valid_Right_Request

1. **Test ID:** `LDM_TC_002`
2. **Testcase name:** `Valid_Right_Request`
3. **Test description:** Enabled LDM with RIGHT risk, valid inputs, no turn signal, and no driver override; mitigation should be permitted.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Positive`
6. **Expected output:** `status=MitigationAllowed; requestMitigation=true; requestedSide=RIGHT; reason=MitigationAllowed`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Baseline positive path.

### LDM_TC_003 - Ldm_Disabled_Inhibit

1. **Test ID:** `LDM_TC_003`
2. **Testcase name:** `Ldm_Disabled_Inhibit`
3. **Test description:** When LDM is disabled, no request should be issued even if departure risk is present.
4. **Clear input:** `enabled=false; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Negative`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=LdmDisabled`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Checks the disabled rule.

### LDM_TC_004 - Speed_Out_Of_Range_Inhibit

1. **Test ID:** `LDM_TC_004`
2. **Testcase name:** `Speed_Out_Of_Range_Inhibit`
3. **Test description:** When speed is outside the configured training range, mitigation must be inhibited.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=false; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Negative`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=SpeedOutOfRange`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Checks the speed gate.

### LDM_TC_005 - No_Risk_Inhibit

1. **Test ID:** `LDM_TC_005`
2. **Testcase name:** `No_Risk_Inhibit`
3. **Test description:** When risk is NONE, no mitigation request is allowed.
4. **Clear input:** `enabled=true; risk=NONE; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Negative`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=NoDepartureRisk`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Covers the no-departure-risk branch.

### LDM_TC_006 - Matching_Left_Signal_Inhibit

1. **Test ID:** `LDM_TC_006`
2. **Testcase name:** `Matching_Left_Signal_Inhibit`
3. **Test description:** When LEFT risk matches an active left turn signal, mitigation must be inhibited.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=true; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Negative`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=MatchingTurnSignal`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Checks matching signal inhibition for LEFT risk.

### LDM_TC_007 - Matching_Right_Signal_Inhibit

1. **Test ID:** `LDM_TC_007`
2. **Testcase name:** `Matching_Right_Signal_Inhibit`
3. **Test description:** When RIGHT risk matches an active right turn signal, mitigation must be inhibited.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=true; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Negative`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=MatchingTurnSignal`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Checks matching signal inhibition for RIGHT risk.

### LDM_TC_008 - Driver_Override_Inhibit

1. **Test ID:** `LDM_TC_008`
2. **Testcase name:** `Driver_Override_Inhibit`
3. **Test description:** If driver override is true, mitigation must be suppressed.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=true; inputValid=true; inputFresh=true`
5. **Testcase type:** `Negative`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=DriverOverride`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Checks the driver-override gate.

### LDM_TC_009 - Invalid_Input_Unavailable

1. **Test ID:** `LDM_TC_009`
2. **Testcase name:** `Invalid_Input_Unavailable`
3. **Test description:** Invalid input must produce unavailable status and no mitigation request.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=false; inputFresh=true`
5. **Testcase type:** `Invalid Input`
6. **Expected output:** `status=InputUnavailable; requestMitigation=false; reason=InputInvalid`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Highest-priority invalid-data test.

### LDM_TC_010 - Stale_Input_Degraded

1. **Test ID:** `LDM_TC_010`
2. **Testcase name:** `Stale_Input_Degraded`
3. **Test description:** Stale input must produce degraded status and no mitigation request.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=false`
5. **Testcase type:** `Stale Input`
6. **Expected output:** `status=Degraded; requestMitigation=false; reason=InputStale`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Checks input freshness handling.

### LDM_TC_011 - Priority_Invalid_Overrides_All

1. **Test ID:** `LDM_TC_011`
2. **Testcase name:** `Priority_Invalid_Overrides_All`
3. **Test description:** Invalid input must win over stale, disabled, speed, risk, signal, and driver-override conditions.
4. **Clear input:** `enabled=false; risk=NONE; speedInTrainingRange=false; leftTurnSignalOn=true; rightTurnSignalOn=true; driverOverride=true; inputValid=false; inputFresh=false`
5. **Testcase type:** `Priority`
6. **Expected output:** `status=InputUnavailable; requestMitigation=false; reason=InputInvalid`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Confirms invalid-input priority.

### LDM_TC_012 - Priority_Stale_Overrides_Disabled

1. **Test ID:** `LDM_TC_012`
2. **Testcase name:** `Priority_Stale_Overrides_Disabled`
3. **Test description:** Stale input must win over disabled state and later inhibit conditions.
4. **Clear input:** `enabled=false; risk=LEFT; speedInTrainingRange=false; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=false`
5. **Testcase type:** `Priority`
6. **Expected output:** `status=Degraded; requestMitigation=false; reason=InputStale`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Confirms stale-input precedence.

### LDM_TC_013 - Priority_Disabled_Overrides_NoRisk

1. **Test ID:** `LDM_TC_013`
2. **Testcase name:** `Priority_Disabled_Overrides_NoRisk`
3. **Test description:** If LDM is disabled, the disabled reason must be returned before risk and signal checks.
4. **Clear input:** `enabled=false; risk=NONE; speedInTrainingRange=true; leftTurnSignalOn=true; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Priority`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=LdmDisabled`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Verifies disabled-state precedence.

### LDM_TC_014 - Priority_Speed_Over_NoRisk

1. **Test ID:** `LDM_TC_014`
2. **Testcase name:** `Priority_Speed_Over_NoRisk`
3. **Test description:** If speed is out of range, the speed reason must be returned before no-risk or signal checks.
4. **Clear input:** `enabled=true; risk=NONE; speedInTrainingRange=false; leftTurnSignalOn=true; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Priority`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=SpeedOutOfRange`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Verifies speed-gate precedence.

### LDM_TC_015 - Priority_Signal_Over_Override

1. **Test ID:** `LDM_TC_015`
2. **Testcase name:** `Priority_Signal_Over_Override`
3. **Test description:** A matching turn signal must take precedence over driver override when both conditions are true.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=true; rightTurnSignalOn=false; driverOverride=true; inputValid=true; inputFresh=true`
5. **Testcase type:** `Priority`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=MatchingTurnSignal`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Confirms matching-signal precedence.

### LDM_TC_016 - Boundary_Min_Valid_Speed

1. **Test ID:** `LDM_TC_016`
2. **Testcase name:** `Boundary_Min_Valid_Speed`
3. **Test description:** At the minimum valid speed boundary, mitigation must remain allowed when all other conditions pass.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Boundary`
6. **Expected output:** `status=MitigationAllowed; requestMitigation=true; requestedSide=LEFT; reason=MitigationAllowed`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Lower-speed boundary. The current MVP represents speed as a boolean range gate.

### LDM_TC_017 - Boundary_Max_Valid_Speed

1. **Test ID:** `LDM_TC_017`
2. **Testcase name:** `Boundary_Max_Valid_Speed`
3. **Test description:** At the maximum valid speed boundary, mitigation must remain allowed when all other conditions pass.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Boundary`
6. **Expected output:** `status=MitigationAllowed; requestMitigation=true; requestedSide=RIGHT; reason=MitigationAllowed`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Upper-speed boundary. The current MVP represents speed as a boolean range gate.

### LDM_TC_018 - Boundary_Just_Below_Min_Speed

1. **Test ID:** `LDM_TC_018`
2. **Testcase name:** `Boundary_Just_Below_Min_Speed`
3. **Test description:** A speed just below the minimum valid speed must be treated as out of range.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=false; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Boundary`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=SpeedOutOfRange`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Negative lower-speed boundary. The input model expresses this as `speedInTrainingRange=false`.

### LDM_TC_019 - Boundary_Just_Above_Max_Speed

1. **Test ID:** `LDM_TC_019`
2. **Testcase name:** `Boundary_Just_Above_Max_Speed`
3. **Test description:** A speed just above the maximum valid speed must be treated as out of range.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=false; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Boundary`
6. **Expected output:** `status=MitigationInhibited; requestMitigation=false; reason=SpeedOutOfRange`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Negative upper-speed boundary. The input model expresses this as `speedInTrainingRange=false`.

### LDM_TC_020 - Freshness_Threshold_Valid

1. **Test ID:** `LDM_TC_020`
2. **Testcase name:** `Freshness_Threshold_Valid`
3. **Test description:** At the configured freshness boundary, the input remains fresh and normal decision evaluation is permitted.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Edge`
6. **Expected output:** `status=MitigationAllowed; requestMitigation=true; requestedSide=LEFT; reason=MitigationAllowed`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Freshness edge. The current MVP represents freshness as a boolean flag.

### LDM_TC_021 - Freshness_Threshold_Expired

1. **Test ID:** `LDM_TC_021`
2. **Testcase name:** `Freshness_Threshold_Expired`
3. **Test description:** Just beyond the freshness threshold, the input must be treated as stale and mitigation must be blocked.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=false`
5. **Testcase type:** `Edge`
6. **Expected output:** `status=Degraded; requestMitigation=false; reason=InputStale`
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Stale freshness edge. The current MVP represents freshness as a boolean flag.

### LDM_TC_022 - Deterministic_Repeated_Evaluation

1. **Test ID:** `LDM_TC_022`
2. **Testcase name:** `Deterministic_Repeated_Evaluation`
3. **Test description:** The same snapshot evaluated repeatedly must produce the same decision every time.
4. **Clear input:** `enabled=true; risk=LEFT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Determinism`
6. **Expected output:** `status=MitigationAllowed; requestMitigation=true; requestedSide=LEFT; reason=MitigationAllowed` on every repeated call.
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Repeat the same input at least twice and compare all output fields.

### LDM_TC_023 - Input_Immutability

1. **Test ID:** `LDM_TC_023`
2. **Testcase name:** `Input_Immutability`
3. **Test description:** The input snapshot must remain unchanged after `evaluateLdm` is called.
4. **Clear input:** `enabled=true; risk=RIGHT; speedInTrainingRange=true; leftTurnSignalOn=false; rightTurnSignalOn=false; driverOverride=false; inputValid=true; inputFresh=true`
5. **Testcase type:** `Immutability`
6. **Expected output:** No mutation of any input field; output remains constant.
7. **Actual output:**
8. **Automated (yes/no):** `yes`
9. **Comments:** Compare every input field before and after evaluation.

## 4. Coverage Summary

The detailed design covers:

- positive LEFT and RIGHT mitigation requests
- disabled LDM
- speed in-range and out-of-range decisions
- risk `NONE`
- matching turn signals
- driver override
- invalid and stale input
- priority ordering for combined inhibit conditions
- minimum and maximum speed boundaries as represented by the current boolean speed gate
- freshness boundary behavior
- deterministic repeated evaluation
- input immutability
