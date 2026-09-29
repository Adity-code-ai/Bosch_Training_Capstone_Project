# LDM Component Test Case Design

## 1. Purpose

This document defines the component-level test design for the pure ASW Lane Departure Mitigation (LDM) decision function. It is aligned with `docs/ut-test-design/ldm-ut-test-design.csv` and the current C++ interface and implementation.

The tests verify:

- deterministic allow or inhibit behavior for one input snapshot
- exact decision status, mitigation request, requested side, and reason code
- input-validity and freshness handling
- speed-range and turn-signal rules
- driver override behavior
- reason-code priority ordering
- input immutability

Transport, HTTP, AWS, actuator, vehicle-integration, and production-safety concerns are out of scope.

## 2. Test Target

The component under test is:

```cpp
ldm::LdmDecision ldm::evaluateLdm(const ldm::LdmInput& input);
```

The function is expected to be pure and stateless. It evaluates one snapshot, returns one decision, and does not modify the input.

## 3. Input and Output Contract

### Input

```cpp
struct LdmInput {
    bool enabled;
    Risk risk;
    bool speedInTrainingRange;
    bool leftTurnSignalOn;
    bool rightTurnSignalOn;
    bool driverOverride;
    bool inputValid;
    bool inputFresh;
};
```

Valid risk values are `None`, `Left`, and `Right`.

### Output

```cpp
struct LdmDecision {
    DecisionStatus status;
    bool requestMitigation;
    Risk requestedSide;
    Reason reason;
};
```

The CSV uses the corresponding textual values `NONE`, `LEFT`, `RIGHT`, `true`, and `false`.

## 4. Decision Priority

The first applicable rule determines the output:

1. `inputValid == false` -> `InputUnavailable`, `InputInvalid`
2. `inputFresh == false` -> `Degraded`, `InputStale`
3. `enabled == false` -> `MitigationInhibited`, `LdmDisabled`
4. `speedInTrainingRange == false` -> `MitigationInhibited`, `SpeedOutOfRange`
5. `risk == None` -> `MitigationInhibited`, `NoDepartureRisk`
6. Matching turn signal active -> `MitigationInhibited`, `MatchingTurnSignal`
7. `driverOverride == true` -> `MitigationInhibited`, `DriverOverride`
8. `risk == Left` or `risk == Right` -> `MitigationAllowed`, `MitigationAllowed`
9. Unsupported risk value -> `MitigationInhibited`, `Unknown`

All inhibited results must have `requestMitigation=false` and `requestedSide=None`. Allowed results must identify the requested risk side.

## 5. Test Execution Approach

Use direct calls to `evaluateLdm()` with table-driven or GoogleTest parameterized inputs. Every ordinary single-snapshot case should assert:

- `status`
- `requestMitigation`
- `requestedSide` when it is specified in the CSV expected output
- `reason`

For `LDM_TC_022`, call the function repeatedly with the same snapshot and compare every output field. For `LDM_TC_023`, copy the input before evaluation and compare every input field after evaluation.

The CSV is the authoritative test-case list. `actual output` is intentionally blank because the CSV is a design-time artifact.

## 6. Test Case Traceability

| Test ID | Scenario | Type | Expected result |
| --- | --- | --- | --- |
| LDM_TC_001 | Valid LEFT request | Positive | Allowed, request `true`, side `LEFT`, reason `MitigationAllowed` |
| LDM_TC_002 | Valid RIGHT request | Positive | Allowed, request `true`, side `RIGHT`, reason `MitigationAllowed` |
| LDM_TC_003 | LDM disabled | Negative | Inhibited, request `false`, reason `LdmDisabled` |
| LDM_TC_004 | Speed out of range | Negative | Inhibited, request `false`, reason `SpeedOutOfRange` |
| LDM_TC_005 | No departure risk | Negative | Inhibited, request `false`, reason `NoDepartureRisk` |
| LDM_TC_006 | Matching LEFT signal | Negative | Inhibited, request `false`, reason `MatchingTurnSignal` |
| LDM_TC_007 | Matching RIGHT signal | Negative | Inhibited, request `false`, reason `MatchingTurnSignal` |
| LDM_TC_008 | Driver override | Negative | Inhibited, request `false`, reason `DriverOverride` |
| LDM_TC_009 | Invalid input | Invalid Input | Input unavailable, request `false`, reason `InputInvalid` |
| LDM_TC_010 | Stale input | Stale Input | Degraded, request `false`, reason `InputStale` |
| LDM_TC_011 | Invalid over stale | Priority | `InputInvalid` wins |
| LDM_TC_012 | Stale over disabled and later rules | Priority | `InputStale` wins |
| LDM_TC_013 | Disabled over other inhibits | Priority | `LdmDisabled` wins |
| LDM_TC_014 | Speed over no-risk and later rules | Priority | `SpeedOutOfRange` wins |
| LDM_TC_015 | Matching signal over override | Priority | `MatchingTurnSignal` wins |
| LDM_TC_016 | Minimum valid speed gate | Boundary | Allowed LEFT request |
| LDM_TC_017 | Maximum valid speed gate | Boundary | Allowed RIGHT request |
| LDM_TC_018 | Below minimum speed gate | Boundary | Inhibited, reason `SpeedOutOfRange` |
| LDM_TC_019 | Above maximum speed gate | Boundary | Inhibited, reason `SpeedOutOfRange` |
| LDM_TC_020 | Freshness boundary valid | Edge | Fresh input allows LEFT request |
| LDM_TC_021 | Freshness boundary expired | Edge | Degraded, request `false`, reason `InputStale` |
| LDM_TC_022 | Repeated evaluation | Determinism | Identical output on repeated calls |
| LDM_TC_023 | Input immutability | Immutability | All input fields unchanged |

## 7. CSV Coverage Notes

The CSV provided with this document ends at `LDM_TC_023`. It includes the following explicit edge and non-functional checks:

- `LDM_TC_020` covers a valid fresh-input boundary.
- `LDM_TC_021` covers an expired freshness boundary and expects `Degraded` with `InputStale`.
- `LDM_TC_022` covers deterministic repeated evaluation.
- `LDM_TC_023` covers input immutability.

The implementation supports the defensive `Unknown` reason for an unsupported enum value, but that fallback is not represented in the attached CSV and is therefore not claimed as covered by this document.

## 8. Coverage and Validation Checklist

- [x] Positive LEFT and RIGHT requests
- [x] LDM disabled
- [x] Speed in-range and out-of-range gate
- [x] Risk `NONE`
- [x] Matching LEFT and RIGHT signals
- [x] Driver override
- [x] Invalid input
- [x] Disabled, speed, risk, signal, and override priority cases
- [x] Boundary cases represented by the current boolean speed-range interface
- [x] Deterministic repeated evaluation (`LDM_TC_022`)
- [x] Input immutability (`LDM_TC_023`)
- [x] CSV design-time `actual output` fields remain blank

## 9. Source of Truth

The authoritative test data is maintained in:

`docs/ut-test-design/ldm-ut-test-design.csv`

The C++ decision contract is defined in:

- `include/ldm/decision.hpp`
- `src/core/decision.cpp`
