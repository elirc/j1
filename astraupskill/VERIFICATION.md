# Verification and practical limits

The completed verification passed **43 checks**: 35 Java model, repository, and service tests plus eight real process checks. The source and tests compiled with JDK 17 (Microsoft Build of OpenJDK 17.0.10, the JDK on the delivery machine; any 17+ works) using UTF-8 and `--release 17`. Python 3 orchestrated the process scenarios in a helper-owned temporary directory. No personal task file was opened or rewritten during verification.

## Executed behavior

The Java suite checks trimmed and bounded text, control-character rejection, positive IDs and versions, completion timestamp consistency, immutable edits, reopen behavior, version exhaustion, and read-only loading of an absent file. Snapshot tests cover Unicode and delimiter round trips, unique identities, allocation watermarks, truncation, trailer counts, malformed UTF-8, and the 8 MiB input bound.

Legacy tests cover complete records, unknown and duplicate fields, invalid booleans and dates, missing closing separators, and duplicate task IDs. Conversion tests verify that original bytes are retained in a legacy backup and that a different existing backup blocks replacement. These are strict conversion checks, not a claim that arbitrary damaged files can be repaired automatically.

Service and repository tests verify immediate persistence, edit/complete/reopen/delete workflows, durable ID allocation after deletion and restart, stale task versions, stale file baselines, external file changes, failed reload, immutable returned lists, and watermark monotonicity. An injected atomic-replacement failure independently checks that both the old file and the manager's accepted task list remain unchanged.

The eight process checks exercise create followed by EOF, restart and list, cancelled deletion, edit/reopen/search, incomplete-command EOF, confirmed deletion, malformed startup, and two competing JVMs. In the final concurrency scenario, both processes load before either is allowed to save; exactly one accepts its change and the other reports a conflict. This demonstrates coordination beyond one process's synchronized methods.

## Reproduce the run

Run `python scripts/verify.py` from the project folder with JDK 17 and Python 3 available. Set `JAVA_HOME` if needed. Logs and JSON evidence are written to `.verification` unless `TODO_VERIFY_RESULTS_DIR` selects another location. The first process run encountered a 15-second startup deadline during a period of slow shell responses. The final run used a 60-second process deadline and passed all unchanged behavioral assertions. The timeout was not counted as a passing CLI check.

## Limits that remain

This is a local Java CLI, with no HTTP API, browser interface, authentication, ownership model, audit history, or deployed SQL database. The course's web and relational-storage exercises are proposed extensions, not implemented features. Rejected terminal edits are not retained as separate drafts; after a conflict, Reload and deliberate re-entry are required.

File coordination is cooperative and depends on participating writers retaining the same sibling lock path. Unrelated programs can ignore that protocol. Atomic replacement must be supported by the filesystem; the application deliberately rejects unsupported replacement instead of falling back to truncation. Flushing the temporary file and atomically replacing the target is useful durability evidence, but this run did not certify power-loss recovery, directory metadata persistence, network filesystem behavior, or multi-machine coordination. Keep these boundaries in a review alongside the passing tests.

## Status note (2026-10-06)

The record above is the original delivery run and is kept as written. On 2026-10-06 the Java suite was re-run with JDK 17.0.10. Source and tests were compiled into a scratch directory outside the repository, and the run printed `RESULT {"passed":true,"tests":35}`. The count of 35 matches the `test(...)` calls in `TaskWorkflowTest.java`. The eight process checks in `scripts/verify.py` were not re-run because that script writes `.verification/` into the working tree. Equivalent CLI scenarios (cancelled delete, stale second session plus Reload, malformed startup) passed through the `node --test` harness in [05-PRACTICE](05-PRACTICE.md), Exercise 1. The defects listed in [06's senior findings](06-SOLUTIONS-AND-REVIEW.md#senior-findings-in-the-delivered-code) were reproduced in the same session. None of them contradicts a guarantee stated here.
