# Lane Departure Mitigation (LDM) MVP Software Design

## 1. Purpose

This document describes the software design for the training MVP that evaluates a single synthetic lane-departure snapshot and decides whether a mitigation request may be issued. The design follows the use case and acceptance criteria defined in the MVP brief and keeps the decision logic separate from the synthetic demo adapter used for AWS training deployment.

The solution is intentionally narrow and deterministic:

- It evaluates one snapshot at a time.
- It does not retain state between calls.
- It is designed as a portable ASW component and a thin demo shell.
- It is explicitly not a production vehicle safety implementation.

---

## 2. Design Goals

### 2.1 Primary goals

1. Evaluate lane-departure risk, driver intent, vehicle state, and input validity in a single, deterministic pass.
2. Return exactly one decision per snapshot with a stable reason code.
3. Allow mitigation only when all required conditions are satisfied.
4. Keep the core decision logic independent from HTTP, JSON, AWS, and environment configuration.
5. Support unit testing for every decision branch, boundary values, and priority-order cases.

### 2.2 Non-goals

- Lane-mark detection or path prediction.
- Steering control or actuator output.
- ECU, CAN, or vehicle runtime integration.
- Production safety certification or vehicle calibration.
- Persistent state, session tracking, or historical reasoning.

---

## 3. Scope and Context

The system receives a snapshot that includes:

- LDM enablement state
- Lane-departure risk: NONE, LEFT, RIGHT
- Vehicle speed and whether it is within the configured training operating range
- Left/right turn-signal state
- Driver override state
- Input validity and freshness

The output is a decision object that includes:

- Decision status
- Whether a mitigation request is issued
- Requested side, when applicable
- Reason code

This is a pure logic component with a thin API boundary, not an embedded software platform or production control application.

---

## 4. Architectural Overview

The architecture follows a functional-core, imperative-shell pattern.

### 4.1 Functional core

The core component is responsible for:

- accepting a typed input snapshot
- validating the relevant business conditions
- evaluating the decision rules
- returning a decision result without depending on transport or cloud frameworks

This component is pure and stateless: it does not read clocks, environment variables, or external services, and it does not mutate the input.

### 4.2 Imperative shell

The shell or adapter layer is responsible for:

- parsing incoming demo payloads
- mapping JSON or HTTP request data into typed input objects
- invoking the core evaluation function
- serializing the response back to the demo caller

This layer may be implemented as an AWS Lambda handler or a simple HTTP wrapper, but it must not duplicate business logic.

### 4.3 High-level component boundaries

```text
Synthetic input payload
        |
        v
Demo adapter / HTTP boundary
        |
        v
Request validation + mapping
        |
        v
Core LDM decision function
        |
        v
Decision result + reason code
        |
        v
Demo serialization / response
```

---

## 5. Detailed Functional Design

## 5.1 Input model

The core input is represented as an immutable data object. It should be passed by value or `const` reference to avoid mutation.

```cpp
enum class Risk {
    None,
    Left,
    Right
};

enum class LdmDecisionStatus {
    MitigationAllowed,
    MitigationInhibited,
    InputUnavailable,
    Degraded
};

enum class LdmReason {
    MitigationAllowed,
    LdmDisabled,
    InputInvalid,
    InputStale,
    SpeedOutOfRange,
    NoDepartureRisk,
    MatchingTurnSignal,
    DriverOverride,
    Unknown
};

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

### 5.2 Output model

```cpp
struct LdmDecision {
    LdmDecisionStatus status;
    bool requestMitigation;
    Risk requestedSide;
    LdmReason reason;
};
```

### 5.3 Reason-code priority principle

The MVP requires a stable reason code that identifies the decision or the first applicable inhibit condition, using an agreed and tested priority order. The design chooses this priority:

1. Input invalid
2. Input stale
3. LDM disabled
4. Speed out of range
5. No departure risk
6. Matching turn signal
7. Driver override
8. Mitigation allowed

This rule is implemented as a priority-ordered evaluation sequence. The first applicable condition wins.

### 5.4 Decision rules

A mitigation request is allowed only when all of the following are true:

- LDM is enabled
- Input is valid
- Input is fresh
- Speed is within training range
- Risk is LEFT or RIGHT
- The matching turn signal is not active
- Driver is not overriding

If any inhibit condition applies, the system must return no mitigation request and the matching reason code.

If the risk is NONE, mitigation is never allowed.

If inputs are invalid or stale, result status is unavailable/degraded and no request is issued.

---

## 6. Decision Algorithm

The core evaluator follows a strict ordered decision ladder.

### 6.1 Pseudocode

```cpp
LdmDecision evaluateLdm(const LdmInput& input) {
    // 1. Hard invalid / stale handling
    if (!input.inputValid) {
        return { LdmDecisionStatus::InputUnavailable, false, Risk::None, LdmReason::InputInvalid };
    }

    if (!input.inputFresh) {
        return { LdmDecisionStatus::Degraded, false, Risk::None, LdmReason::InputStale };
    }

    // 2. System disabled or operating condition blocked
    if (!input.enabled) {
        return { LdmDecisionStatus::MitigationInhibited, false, Risk::None, LdmReason::LdmDisabled };
    }

    if (!input.speedInTrainingRange) {
        return { LdmDecisionStatus::MitigationInhibited, false, Risk::None, LdmReason::SpeedOutOfRange };
    }

    // 3. No departure risk
    if (input.risk == Risk::None) {
        return { LdmDecisionStatus::MitigationInhibited, false, Risk::None, LdmReason::NoDepartureRisk };
    }

    // 4. Matching signal inhibit
    if ((input.risk == Risk::Left && input.leftTurnSignalOn) ||
        (input.risk == Risk::Right && input.rightTurnSignalOn)) {
        return { LdmDecisionStatus::MitigationInhibited, false, Risk::None, LdmReason::MatchingTurnSignal };
    }

    // 5. Driver override inhibit
    if (input.driverOverride) {
        return { LdmDecisionStatus::MitigationInhibited, false, Risk::None, LdmReason::DriverOverride };
    }

    // 6. Allow only if the side is explicitly left or right
    if (input.risk == Risk::Left) {
        return { LdmDecisionStatus::MitigationAllowed, true, Risk::Left, LdmReason::MitigationAllowed };
    }

    if (input.risk == Risk::Right) {
        return { LdmDecisionStatus::MitigationAllowed, true, Risk::Right, LdmReason::MitigationAllowed };
    }

    return { LdmDecisionStatus::MitigationInhibited, false, Risk::None, LdmReason::Unknown };
}
```

### 6.2 Why the ordered approach matters

The design intentionally evaluates the input in a fixed order so that:

- invalid data is never masked by later rules
- a single snapshot produces one deterministic outcome
- multiple inhibit conditions produce the same stable result every time
- tests can assert exact reason codes and priority behavior

---

## 7. Rule Justification and Priority

The priority is chosen to match the functional intent and acceptance criteria:

| Priority | Condition | Reason code | Why first |
| --- | --- | --- | --- |
| 1 | Input invalid | `InputInvalid` | Data quality matters more than any operational decision |
| 2 | Input stale | `InputStale` | Freshness is essential before evaluating any motion or driver state |
| 3 | LDM disabled | `LdmDisabled` | System cannot issue a request when disabled |
| 4 | Speed out of range | `SpeedOutOfRange` | Operating condition is outside configured training envelope |
| 5 | No departure risk | `NoDepartureRisk` | No trigger means no request |
| 6 | Matching turn signal | `MatchingTurnSignal` | Driver intent prevents mitigation |
| 7 | Driver override | `DriverOverride` | Human intervention should suppress automated request |
| 8 | Allowed | `MitigationAllowed` | Only when all required conditions are satisfied |

This order is explicit and testable. It is not a claim about production safety logic.

---

## 8. Data and Functional Contracts

### 8.1 Input validation rules

The adapter boundary validates and normalizes raw data before handing it to the core component.

- `enabled` must be a boolean.
- `risk` must be one of `NONE`, `LEFT`, or `RIGHT`.
- `speedInTrainingRange` must be boolean.
- `leftTurnSignalOn` and `rightTurnSignalOn` must be booleans.
- `driverOverride` must be boolean.
- `inputValid` and `inputFresh` must be boolean.

The core function assumes the input has already been validated to the required shape and types. It does not try to repair malformed data.

### 8.2 Input immutability

The core function must not mutate any member of the input object. The function signature should accept `const LdmInput&` and all internally derived values should be local variables.

This requirement supports deterministic behavior and simplifies testing.

### 8.3 Pure function contract

The function contract is:

- deterministic for a given input
- no side effects
- no retained state
- no dependency on wall-clock time or external configuration beyond explicit parameters

---

## 9. Configuration Design

The system is designed to accept explicit configuration rather than hard-coded assumptions.

```cpp
struct LdmConfiguration {
    double minimumSpeed;
    double maximumSpeed;
    std::chron::milliseconds freshnessThreshold;
};
```

### 9.1 Why explicit configuration matters

This keeps the logic portable and testable. Training values are not production calibration values and should be clearly tagged as such in code comments and documentation.

### 9.2 Example configuration

```cpp
constexpr LdmConfiguration kTrainingConfig{
    .minimumSpeed = 20.0,
    .maximumSpeed = 120.0,
    .freshnessThreshold = std::chrono::milliseconds{2000}
};
```

The adapter may provide values received from environment or config files, but the core should accept them as arguments to ensure explicit behavior and easier test injection.

---

## 10. API Boundary and Demo Adapter Design

The demo adapter is the shell that receives synthetic requests and calls the core function. It is deliberately thin.

### 10.1 REST contract (training demo)

| Method | Path | Action |
| --- | --- | --- |
| `POST` | `/evaluate` | Evaluate one snapshot and return a decision object |

### 10.2 Example request payload

```json
{
  "enabled": true,
  "risk": "LEFT",
  "speedInTrainingRange": true,
  "leftTurnSignalOn": false,
  "rightTurnSignalOn": false,
  "driverOverride": false,
  "inputValid": true,
  "inputFresh": true
}
```

### 10.3 Example response payload

```json
{
  "status": "MITIGATION_ALLOWED",
  "requestMitigation": true,
  "requestedSide": "LEFT",
  "reason": "MITIGATION_ALLOWED"
}
```

### 10.4 Adapter responsibilities

- parse request body
- validate well-formedness and required fields
- map payload fields to `LdmInput`
- call `evaluateLdm(input)`
- serialize the returned `LdmDecision` into JSON
- return appropriate HTTP status codes for invalid requests or adapter-level errors

### 10.5 Adapter non-responsibilities

- no rule evaluation logic
- no reason-code priority logic
- no state persistence
- no direct production interface assumptions

---

## 11. Error and Degraded Handling

The design treats invalid or stale input as a degraded state rather than a normal decision.

### 11.1 Input invalid

When `inputValid == false`, the function returns:

- `status = InputUnavailable`
- `requestMitigation = false`
- `reason = InputInvalid`

This prevents any invalid data from causing a request.

### 11.2 Input stale

When `inputFresh == false`, the function returns:

- `status = Degraded`
- `requestMitigation = false`
- `reason = InputStale`

### 11.3 `NONE` risk and inhibit cases

All inhibit scenarios also return `requestMitigation = false` with the relevant reason code.

---

## 12. Testing Strategy

Testing is required for all decision branches and boundary conditions.

### 12.1 Unit test categories

1. Allowed mitigation requests
2. Single inhibit conditions
3. Invalid and stale inputs
4. Boundary values for speed and freshness
5. Reason priority when multiple inhibits apply
6. Deterministic repeated evaluation
7. Input immutability

### 12.2 Example test scenarios

- enabled = true, risk = LEFT, all other inputs valid, request should be allowed
- risk = NONE should inhibit with `NoDepartureRisk`
- LDM disabled should inhibit with `LdmDisabled`
- speed out of range should inhibit with `SpeedOutOfRange`
- matching left turn signal with left risk should inhibit with `MatchingTurnSignal`
- driver override should inhibit with `DriverOverride`
- invalid input should return `InputUnavailable`
- stale input should return `Degraded`
- repeated same snapshot should yield the same result
- function should not change any input field

### 12.3 Priority testing

A critical design check is verifying that when more than one inhibit condition applies, the first condition in the priority order wins. Example:

- LDM disabled + risk NONE + turn signal on + stale input
- expected result should be `InputStale` if stale check occurs before other rules

This makes the rule sequence both deterministic and reviewable.

---

## 13. Error Handling and Defensive Design

The primary safety behavior here is not a vehicle safety boundary; it is a conservative software rule set. Defensive measures in the design include:

- no hidden global state
- no mutation of input parameters
- strict typed enums instead of string-driven decisions
- explicit reason codes
- early exits for invalid or stale data
- single return path with stable output structure

This supports readability and reviewability, especially in a Copilot-assisted development workflow.

---

## 14. Component Interaction Model

### 14.1 Core component

- Inputs: structured `LdmInput`
- Outputs: structured `LdmDecision`
- Dependencies: none beyond standard C++ and explicit config objects
- Scope: decision logic only

### 14.2 Demo adapter

- Inputs: HTTP or Lambda request payload
- Outputs: JSON response envelope
- Dependencies: web framework, JSON serialization, lambda runtime, or thin transport handling
- Scope: validation, mapping, serialization, not business rules

---

## 15. Recommended Implementation Layout

```text
include/
  ldm/
    decision.hpp
    model.hpp
    config.hpp
src/
  core/
    decision.cpp
  adapter/
    aws/
      lambda_handler.cpp
      request_mapper.cpp
tests/
  unit/
    decision_test.cpp
  adapter/
    lambda_adapter_test.cpp
```

This structure keeps the portable logic independent from the AWS training layer.

---

## 16. Design Risks and Limitations

This design intentionally acknowledges the limitations of the MVP:

- It is not a production-grade safety function.
- It does not model all input validity nuances of a real vehicle.
- It assumes deterministic synthetic data and explicit configuration values.
- It is a training artifact, not an approved runtime design for in-vehicle deployment.

Those limitations are part of the design and must remain visible in documentation and code comments.

---

## 17. Summary

The software is designed as a small, pure decision engine with a strict priority-ordered rule set and a thin synthetic adapter. The core is deterministic, stateless, and easy to unit test. The adapter translates external input into the core model and returns a structured result without duplicating business logic.

This design matches the MVP requirement to evaluate lane-departure risk, driver intent, validity, freshness, and speed in a controlled training environment while preserving a clear separation between the portable decision component and the AWS demo interface.
