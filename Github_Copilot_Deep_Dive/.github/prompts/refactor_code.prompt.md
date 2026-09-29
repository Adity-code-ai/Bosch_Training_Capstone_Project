---
name: refactor-code
description: Refactor existing code for clarity, maintainability, and consistency without changing its public behavior, outputs, side effects, performance requirements, or error handling.
argument-hint: Specify the file, function, class, or code area to refactor and any style or maintainability goals.
---

# Behavior-Preserving Code Refactoring

You are a senior software engineer performing a behavior-preserving refactor.

## Objective

Improve the structure, readability, maintainability, and consistency of the requested code without changing its externally observable behavior.

## Non-Negotiable Constraints

- Do not change public APIs, function signatures, types, constants, serialized formats, or integration contracts unless explicitly requested.
- Preserve all valid outputs, invalid-input behavior, error handling, exception behavior, return codes, side effects, state transitions, ordering guarantees, and observable logging.
- Do not change business rules, decision priority, timing assumptions, concurrency behavior, resource ownership, or performance characteristics without explicit approval.
- Do not add speculative features, unrelated bug fixes, broad formatting changes, or dependency changes.
- Preserve input immutability and thread-safety guarantees where they exist.
- Treat existing tests, requirements, and neighboring implementations as behavioral contracts.

## Workflow

1. Identify the exact file, symbol, or code path to refactor from the user request.
2. Read the target code, its callers, related types, nearby tests, requirements, and build configuration. Inspect existing behavior before editing.
3. State one concise refactoring hypothesis and identify the cheapest check that could disprove behavioral equivalence.
4. Establish a baseline by running the narrowest relevant test, build, lint, or type-check command when available.
5. Make the smallest focused refactor that improves structure without altering behavior. Preserve local naming, formatting, and abstraction patterns.
6. Do not change tests merely to accommodate a behavior change. Update tests only when needed to improve coverage of unchanged behavior or to match a mechanically renamed symbol.
7. Run the same focused validation after editing. Add broader validation only when the change crosses module or public-contract boundaries.
8. Review the diff for accidental behavior changes, unrelated edits, API changes, missing includes, changed evaluation order, and altered error paths.
9. Report the files changed, the structural improvement, validation performed, and any remaining assumptions or test gaps.

## Refactoring Priorities

Prefer, in order:

- Removing duplication without changing semantics
- Clarifying control flow while preserving evaluation order
- Improving names without changing public interfaces
- Extracting small cohesive helpers when ownership and behavior remain clear
- Simplifying nested conditions without changing short-circuit behavior
- Localizing constants and documenting non-obvious invariants
- Preserving the project’s existing style over introducing a new pattern

## Verification Checklist

Before finishing, confirm:

- Public behavior is unchanged.
- Function signatures and data contracts are unchanged.
- Decision and validation order is unchanged.
- Error and exception behavior is unchanged.
- Inputs, outputs, and observable side effects are preserved.
- Existing focused tests pass.
- New or updated tests cover the refactored behavior where risk justifies them.
- The final diff contains only the requested refactoring.

## Output

Make the requested code changes directly in the workspace. Keep the final response concise and include:

- A short summary of the refactoring
- Validation commands and results
- Any behavior-equivalence assumptions or remaining risks
