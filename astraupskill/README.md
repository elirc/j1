# Start here: a small task manager with real consistency problems

This Java project is intentionally small enough to understand end to end. The application manages tasks in a terminal, but its useful lessons transfer directly to CRUD web development: validate input, protect the model, separate interaction from policy, make persistence reliable, and explain what happens when two editors disagree. Use [the root setup guide](../README.md) to compile and run a separate fictional task file.

## Your first hour

Create two tasks, complete one, edit the other, search for open tasks, and cancel a deletion. Then restart the program and confirm that accepted changes remain. Open another terminal against the same file before saving a new task in the first. Try a mutation in the stale second session. It should report a conflict instead of overwriting the first session's work. Reload the current file, inspect it, and deliberately re-enter the change.

Do not use personal task data for failure experiments. The verification helper creates disposable fixtures for corruption, atomic-save failure, and competing processes. The application refuses to replace an unreadable file with an empty list. That behavior is a central improvement over the original starter and a useful example of treating error handling as data protection.

## Reading and practice order

1. Follow [the codebase map](01-CODEBASE-MAP.md). Identify the terminal adapter, service, immutable task value, snapshot, and repository before changing code.
2. Study [the concepts guide](02-CONCEPTS.md). Explain why copying a list is not enough when the objects inside it remain mutable, and why an atomic rename alone does not prevent stale overwrites.
3. Work through [the edit walkthrough](03-WORKED-CHANGE.md). Follow a candidate value from validated input to accepted persistence and only then to in-memory state.
4. Read [testing and debugging](04-TESTING-AND-DEBUGGING.md), run the checks, and inspect a failing scenario in its temporary fixture.
5. Complete [the exercises](05-PRACTICE.md), compare with [review guidance](06-SOLUTIONS-AND-REVIEW.md), and deliver [the trace lab](07-TRACE-LAB.md) explanation.

## What mid-level progress looks like

You should be able to state a guarantee and point to evidence. For example: "A failed atomic replacement leaves the old file unchanged and does not expose the rejected task through the service." That is stronger than saying "The save method has a try/catch." The claim names the failure, durable state, and observable application result.

Similarly, distinguish the current implementation from a future web application. This project does not have authentication or an HTTP endpoint. You can map its version check to a future `If-Match` or expected-version request, but that is a design exercise until implemented and tested. Use [the verification record](VERIFICATION.md) to keep your review accurate.

At the end, prepare a short explanation for another junior engineer: one successful edit, one rejected stale edit, and one failed storage write. Connecting those three stories demonstrates ownership of behavior beyond the happy path.
