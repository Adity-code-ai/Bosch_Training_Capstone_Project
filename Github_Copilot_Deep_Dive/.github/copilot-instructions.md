# ASW Lane Departure Mitigation (LDM) Training MVP

## 1. Project Name

ASW Lane Departure Mitigation Copilot Training MVP

## 2. Description

This repository is a 16-hour GitHub Copilot training exercise for a development team. The MVP models a small, deterministic Lane Departure Mitigation decision function for an in-vehicle application-software context. Given a synthetic vehicle-state snapshot, it returns a mitigation request or an inhibit/unavailable result with a stable reason code.

This is training software only. It does not detect lane markings, calculate steering torque, control actuators, communicate with a vehicle, or provide safety-certified behavior. Any AWS deployment is a synthetic-input demonstration wrapper and must not be connected to vehicle hardware or treated as the in-vehicle runtime architecture. See [the MVP use case](../ASW_LDM_Copilot_Training_MVP.md) for requirements and acceptance criteria.

## 3. Tech Stack Used

No implementation, dependency manifest, or deployment template currently exists in the repository. The following is the **proposed training baseline**, not a claim about already implemented technology:

- Core LDM decision logic: portable C++20 library, independent of cloud and transport code.
- Unit tests: GoogleTest.
- Build: CMake; use CTest to register and run tests.
- Training demo: AWS Lambda C++ runtime behind API Gateway, using AWS SAM for packaging/deployment. Keep its adapter separate from the core library.
- CI/CD: GitHub Actions; use the organization's approved AWS training-account identity, preferably OIDC.

Before implementing, agree and record exact toolchain, dependency, AWS runtime, and SAM CLI versions in the build/dependency files and CI configuration. Keep versions pinned and reproducible; do not silently upgrade dependencies.

## 4. Design Pattern / Architecture

Use a **functional core, imperative shell** architecture (a design direction chosen for this training MVP):

- The core decision function is deterministic, stateless, and has no I/O, cloud SDK, or transport dependency.
- The demo adapter parses and validates requests, calls the core, and serializes the response.
- Configuration such as training speed limits and input freshness thresholds is passed explicitly; do not embed vehicle calibration assumptions in the core.
- The AWS adapter is only a demonstration boundary. Do not add vehicle/ECU/actuator integrations.

## 5. Language Versions, Libraries, and Sources

These are proposed training pins/baselines. They must be confirmed against the team's approved toolchain and committed in manifests or build configuration before use. A version listed here is not evidence that the dependency is already installed.

| Component | Proposed version/baseline | Purpose | Authoritative source |
| --- | --- | --- | --- |
| C++ | C++20 (`-std=c++20`) | Portable LDM decision core | [ISO C++ standards](https://isocpp.org/std/the-standard) |
| CMake | 3.22.1 minimum | Configure and build the core and tests | [CMake 3.22 documentation](https://cmake.org/cmake/help/v3.22/) |
| GoogleTest | 1.14.0 | Unit tests for decision behavior | [GoogleTest v1.14.0 release](https://github.com/google/googletest/releases/tag/v1.14.0) |
| AWS Lambda C++ runtime | Pin a reviewed release before implementation | Invoke the C++ demo adapter in Lambda | [AWS Lambda C++ runtime repository](https://github.com/awslabs/aws-lambda-cpp) |
| AWS SAM CLI | Pin an approved version in the training environment/CI | Package and deploy the demo | [AWS SAM CLI installation and version guidance](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) |
| GoogleTest integration | CMake `FetchContent` at the exact GoogleTest tag, or the organization's approved package mirror | Reproducible test dependency | [GoogleTest quickstart](https://google.github.io/googletest/quickstart-cmake.html) |

Do not add third-party libraries unless the requirement needs them. When adding one, document its exact version, purpose, license review status as required by the organization, and official source in the dependency manifest or this table. Do not copy dependency source into the repository without approval.

## 6. Coding Standard

- Follow the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) and the team's approved automotive C++ rules. If a project-specific standard such as MISRA C++ is required, use its licensed, approved edition and record the deviations process; do not claim compliance without the required checks and evidence.
- Use C++20 consistently and enable compiler warnings for the selected compiler. Treat warnings as errors in CI where the toolchain supports a stable warning set.
- Use `clang-format` with a checked-in `.clang-format` file once the team agrees the format. Do not invent formatting exceptions in individual files.
- Prefer descriptive names, small functions, explicit types, `const` correctness, scoped enums, and clear ownership. Avoid hidden mutable global state and unexplained numeric constants.
- Keep decision rules and inhibit priority explicit. Return stable typed status/reason values; do not use free-form strings as internal decision state.
- Validate external/demo input at the adapter boundary. Keep the core function independent of JSON, HTTP, AWS SDKs, clocks, and environment variables.
- Make changes narrowly, preserve existing behavior unless requirements change, and update tests with behavior changes.
- Copilot-generated code is a draft. Developers are responsible for correctness, safety boundaries, security, licensing review, and maintainability.

## 7. Sample Test Code

Use GoogleTest for the C++ core. This example assumes project types `LdmInput`, `LdmDecision`, `Risk`, and `evaluateLdm`; adapt names to the implementation while preserving the behavior being tested. All values are synthetic training values, not vehicle calibration.

```cpp
#include <gtest/gtest.h>

#include "ldm/decision.hpp"

TEST(LdmDecisionTest, RequestsMitigationForValidLeftDeparture) {
	const LdmInput input{
		.enabled = true,
		.risk = Risk::Left,
		.speedInTrainingRange = true,
		.leftTurnSignalOn = false,
		.rightTurnSignalOn = false,
		.driverOverride = false,
		.inputValid = true,
		.inputFresh = true,
	};

	const LdmDecision result = evaluateLdm(input);

	EXPECT_TRUE(result.requestMitigation);
	EXPECT_EQ(result.requestedSide, Risk::Left);
	EXPECT_EQ(result.reason, LdmReason::MitigationAllowed);
}

TEST(LdmDecisionTest, MatchingTurnSignalInhibitsMitigation) {
	const LdmInput input{
		.enabled = true,
		.risk = Risk::Left,
		.speedInTrainingRange = true,
		.leftTurnSignalOn = true,
		.rightTurnSignalOn = false,
		.driverOverride = false,
		.inputValid = true,
		.inputFresh = true,
	};

	const LdmDecision result = evaluateLdm(input);

	EXPECT_FALSE(result.requestMitigation);
	EXPECT_EQ(result.reason, LdmReason::MatchingTurnSignal);
}
```

Add tests for each inhibit condition, invalid/stale input, speed/freshness boundaries, reason priority when multiple inhibits apply, deterministic repeated calls, and input immutability. Tests must not imply that passing this training suite validates production vehicle safety.

## 8. Folder Structure

The tree below is a **proposed starting layout**, not the current repository contents. Current tracked project material is the MVP brief and this instruction file. Add folders as the implementation is created; do not claim a directory exists until it does.

```text
.
|-- .github/
|   |-- copilot-instructions.md
|   `-- workflows/                 # CI and training deployment workflows
|-- ASW_LDM_Copilot_Training_MVP.md # Training use case and acceptance criteria
|-- include/
|   `-- ldm/                       # Public core types and interface
|-- src/
|   |-- core/                      # Portable decision logic
|   `-- adapter/aws/               # Synthetic-input Lambda/API adapter
|-- tests/
|   |-- unit/                      # Core decision tests
|   `-- adapter/                   # Adapter contract tests
|-- CMakeLists.txt
|-- CMakePresets.json              # Optional, if the team adopts presets
|-- template.yaml                  # AWS SAM template for training demo only
`-- README.md                      # Build, test, deploy, and teardown steps
```

Keep the core buildable and testable without AWS dependencies. Do not commit build output, generated credentials, or local environment files.

## 9. Sensitive Data Handling

- Use synthetic, non-identifying vehicle-state inputs only. Never add customer, driver, VIN, license plate, location history, production telemetry, or proprietary vehicle data to source, tests, examples, prompts, logs, or training artifacts.
- Never commit passwords, access keys, tokens, private keys, certificates, production endpoints, or secrets in source, test fixtures, workflow files, screenshots, or documentation.
- Use the organization's approved secret manager and AWS training-account identity. Prefer short-lived GitHub Actions OIDC credentials over long-lived AWS keys; restrict permissions to the training resources and remove temporary resources after the exercise.
- Keep secrets out of command-line arguments and logs. Redact request data and credentials from errors; do not log full input snapshots unless the data has been reviewed and sanitized.
- Use least privilege, separate training and production accounts, and never point training workflows at production. Do not put secrets in Copilot prompts or chat context.
- If sensitive data or a credential is exposed, stop using it, notify the designated security contact, and follow the organization's incident and rotation procedures. Removing it from the latest commit alone may not remove it from repository history or logs.
