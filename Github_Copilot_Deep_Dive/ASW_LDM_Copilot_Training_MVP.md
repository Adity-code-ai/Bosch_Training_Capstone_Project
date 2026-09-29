# ASW Lane Departure Mitigation Copilot Training: MVP Use Case

## Training goal

In 16 hours of instructor-led concept and hands-on work, a development team will use GitHub Copilot through the lifecycle to analyze, design, implement, test, refactor, review, and deploy a small Lane Departure Mitigation (LDM) function for an in-vehicle application-software context.

The team practices engineering judgment with Copilot; generated code and recommendations must be inspected, tested, and reviewed by the developers.

## Use case: Lane Departure Mitigation Decision

The vehicle application receives a lane-departure risk assessment from an upstream lane/perception function. LDM decides whether conditions allow a mitigation request, or whether it must inhibit the request. This MVP focuses only on that decision logic; it does not detect lane markings or control steering.

For hands-on AWS deployment, a thin demo wrapper accepts synthetic vehicle-state snapshots and calls the same decision logic. AWS hosts the training demo only. It is not connected to a vehicle, ECU, actuator, or production service.

## MVP requirement

**As an in-vehicle application, I want LDM to evaluate lane-departure risk together with driver intent, vehicle state, and input validity, so that it can issue a mitigation request only when the configured training conditions allow it.**

### Inputs and output

The function receives one snapshot containing:

- LDM enabled/disabled state.
- Lane-departure risk: `NONE`, `LEFT`, or `RIGHT`, produced by a simulated upstream function.
- Vehicle speed and whether it is within the configured training operating range.
- Left and right turn-signal states.
- Driver override state.
- Input validity and timestamp/freshness information.

It returns a decision status, whether a mitigation request is issued, the requested side when applicable, and a reason code. The output is an abstract request for a simulated downstream interface, not a steering torque, brake command, or actuator signal.

### Functional requirements

1. Evaluate each input snapshot deterministically and return one decision for that snapshot.
2. Issue a mitigation request only when LDM is enabled, the input is valid and fresh, speed is within the configured training range, a left/right departure risk is present, the matching turn signal is not active, and the driver is not overriding the system.
3. Do not issue a request when risk is `NONE` or any inhibit condition is present.
4. When inputs are invalid or stale, return an unavailable/degraded status and do not issue a request.
5. Return a stable reason code identifying the decision or the first applicable inhibit condition, using an agreed and tested priority order.
6. Do not modify the input snapshot or retain state between calls in this MVP.
7. Keep the decision logic separate from the demo transport so it can be built and unit-tested as an ASW component using the team's normal language and framework.

### Acceptance criteria

- Valid, fresh inputs with enabled LDM, in-range speed, left/right risk, no matching signal, and no driver override produce a mitigation request for the correct side.
- `NONE` risk, disabled LDM, out-of-range speed, matching turn signal, or driver override each suppresses the request and returns the expected reason code.
- Invalid or stale inputs produce an unavailable/degraded result and never produce a request.
- Boundary values for the configured speed range and input freshness are covered by tests.
- Repeated evaluation of the same snapshot produces the same result and does not mutate the snapshot.
- Automated tests cover each decision branch and the agreed priority when multiple inhibit conditions apply.
- The synthetic-input demo can be deployed to a dedicated AWS training environment and exercised without any vehicle or actuator connection.

## Explicitly out of scope

- Lane-marking detection, camera/radar processing, lane geometry, or trajectory prediction.
- Steering torque calculation, brake control, actuator commands, or vehicle network communication.
- ECU integration, real vehicle tests, calibration for a vehicle platform, or production deployment.
- Defining production safety goals, safety mechanisms, diagnostic coverage, or certification evidence. This training MVP is not production-ready or safety-certified.
- Production cybersecurity, availability, resilience, or operational on-call design.
- Product discovery, formal stakeholder sign-off, and release governance. The facilitator supplies the scenario; the development team practices requirement clarification and analysis.

## Suggested implementation boundary

Implement the core decision function in the team's normal ASW language and style as a pure, portable component with no cloud or transport dependencies. Add a small synthetic-input demo adapter for AWS. The adapter may be a simple HTTP endpoint and should call the core function rather than duplicate its rules.

The AWS deployment is only a training demonstration of the software build and delivery workflow. Do not deploy software from the exercise to a vehicle or treat the AWS demo as an in-vehicle runtime architecture. Use the organization's approved AWS training account and identity pattern; do not commit long-lived credentials.

Suggested demo operation:

| Method and path | Behavior |
| --- | --- |
| `POST /evaluate` | Validate one synthetic snapshot, call the LDM decision function, and return the decision and reason code |

Keep configuration explicit and testable. The facilitator supplies illustrative training values for speed range and input freshness; these are not vehicle calibration values and must not be represented as suitable for production.

## 16-hour agenda

Hours below are instructional hours; breaks are not counted. Each block combines a short concept segment with a hands-on outcome.

| Time | Stage | Concept focus | Hands-on outcome |
| --- | --- | --- | --- |
| 2 h | Requirement analysis | Function boundary, assumptions, operating conditions, inhibit rules, acceptance criteria, and asking Copilot to find ambiguities | Refine the supplied requirement, agree reason-code priority, and turn acceptance criteria into test scenarios |
| 1.5 h | Design | Pure-function boundary, input/output types, deterministic behavior, configuration, and adapter separation | Sketch the decision table and component boundary; agree a short implementation design |
| 3.5 h | Develop | Small increments, useful Copilot context, code generation versus developer ownership, and implementation checks | Implement the LDM decision function and thin synthetic-input demo adapter |
| 2 h | Test | Unit, boundary, decision-table, and adapter testing; using acceptance criteria as test cases | Add and run automated tests for allowed requests, every inhibit condition, invalid/stale input, and rule priority |
| 1.5 h | Refactor | Readability, explicit decision rules, separation of concerns, and behavior-preserving changes | Refactor one decision area and show that all tests still pass |
| 1 h | Review | Reviewing AI-assisted changes for correctness, unsafe assumptions, maintainability, and test gaps | Review a peer's pull request; resolve findings and summarize limitations |
| 2 h | CI/CD | Pull-request checks, repeatable builds, deployment identity, and secret handling | Add a GitHub Actions workflow for core tests and demo build/deployment using the organization's approved AWS identity pattern, preferably OIDC |
| 2.5 h | Deploy and verify | AWS training environment boundaries, deployment outputs, synthetic smoke tests, and teardown | Deploy the demo wrapper to a non-production training account, submit synthetic snapshots, verify decisions, and remove temporary resources |
| **16 h** | **Total** |  |  |

## Suggested facilitation rhythm

- Start each stage with a short concept demonstration, then have pairs complete the hands-on task.
- Use Copilot Chat to explore and critique alternatives; use inline assistance for small, reviewable changes. Ask participants to explain why they accept, change, or reject suggestions.
- Keep the requirement and acceptance criteria visible throughout. Do not treat generated code as evidence that a criterion is met; tests and observed behavior are the evidence.
- Treat all vehicle-state data as synthetic and all operating values as training examples. Do not connect the demo to vehicle hardware or imply its decision rules are suitable for a vehicle.
- End with a working synthetic demo, a reviewed change, a passing pipeline, and a short list of limitations before considering any production path.

## Completion checklist

- The team can explain the requirement, assumptions, decision table, function interface, and demo boundary.
- The MVP behavior is covered by automated tests and all tests pass locally and in CI.
- At least one refactor and one peer review have been completed.
- The pipeline deploys only the synthetic-input demo to the designated AWS training environment without embedding long-lived AWS keys in the repository.
- A smoke test confirms allowed mitigation requests and representative inhibit decisions using synthetic snapshots.
- The team documents that production use would require vehicle-program requirements, platform integration, calibration, safety engineering and verification, diagnostics, cybersecurity, and formal approval.