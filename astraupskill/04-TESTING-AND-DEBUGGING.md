# Test and debug the file boundary

Run [scripts/verify.py](../scripts/verify.py) with Python 3 and JDK 17 available. The helper compiles the source and tests into a unique temporary directory. It runs the Java workflow suite, exercises the real terminal application with controlled input, and coordinates two independent JVMs. It writes logs and JSON evidence to `.verification` or your chosen `TODO_VERIFY_RESULTS_DIR`.

## Running the verification helper

One command compiles `src/` and `test/` into a fresh temporary directory, runs the workflow suite, drives the real CLI and coordinates the two-JVM scenario. Set `TODO_VERIFY_RESULTS_DIR` when you want the logs somewhere other than `.verification`.

```bash
python scripts/verify.py
TODO_VERIFY_RESULTS_DIR=/tmp/todo-evidence python scripts/verify.py
```

`.verification/` is listed in `.gitignore`, so the evidence never shows up as a change.

## Run only the Java suite (no Python)

`TaskWorkflowTest` has its own `main` and takes a scratch directory for its fixtures. There are no JUnit or other dependencies:

```bash
javac -encoding UTF-8 --release 17 -d "$TMP/todo-classes" $(git ls-files 'src/*.java' 'test/*.java')
java -cp "$TMP/todo-classes" todo.TaskWorkflowTest "$TMP/todo-unit"
```

Each test prints `PASS <name>`, and a full run ends with `RESULT {"passed":true,"tests":35}`. The first failing test throws and stops the run, so the last `PASS` line tells you where to look. Re-run on 2026-10-06 with JDK 17.0.10, the suite gave 35 passes.

The CLI-level checks in [the practice guide](05-PRACTICE.md) use the same idea from Node. `practice/harness.mjs` compiles `src/` into `os.tmpdir()` and pipes menu input into `todo.App`, so you can turn any scenario below into a `node --test` file.

## Use fixtures that make corruption harmless

Never experiment by corrupting your normal task file. The helper creates all data under its owned temporary directory. The startup-failure scenario writes a malformed fixture, starts the CLI, expects a nonzero exit code, and compares the bytes afterward. This establishes that the old "start empty after load error" behavior cannot silently erase a user's file.

The EOF scenario starts a task command and ends input before the description is supplied. It compares the file before and after. Previously accepted tasks remain saved, but the incomplete command is not applied. This checks the interaction boundary, which a direct service call does not exercise.

## Test both memory and durable state

A failed save can produce two different bugs: replacing the disk file despite reporting failure, or exposing rejected data in memory while the disk remains unchanged. The injected atomic-move failure checks both. It saves a known task, loads a manager with a failing repository, attempts another task, and then independently inspects the old bytes and the manager's task list.

For stale edits, assert the accepted title after the rejection. An exception alone does not prove that no assignment happened before it. For malformed legacy records, reject the entire load rather than returning whichever records happened to parse first. The snapshot invariants make partial acceptance inappropriate without an explicit import-review workflow.

## Understand the two-JVM scenario

The helper starts two processes that both load the same missing task file and signal readiness. Only after both have loaded does the helper release a barrier. Each process attempts a save. Exactly one should report acceptance and the other a conflict. This deliberately creates stale baselines and proves coordination beyond a single Java object's `synchronized` methods.

If the scenario fails, inspect the worker outputs and lock path. Confirm that both processes target the same normalized file and retain the same sibling lock file. An unrelated program that ignores the lock is outside this cooperative protocol; do not claim the test proves protection against every possible filesystem writer.

## Debug in a useful order

Identify whether the failure came from input validation, task lookup, task version, snapshot validation, baseline mismatch, backup preservation, or atomic replacement. Read the corresponding log and preserve the fixture before changing code if you need a deeper experiment. Use [the verification record](VERIFICATION.md) to distinguish executed evidence from future ideas such as HTTP integration, database migration, or power-loss certification.
