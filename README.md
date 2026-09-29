# CLI To-Do Manager: dependable CRUD foundations

A small Java 17 task manager with create, list, edit, complete, reopen, search, and confirmed deletion. Read [the detailed learning path](astraupskill/README.md) to connect the code to mid-level CRUD web development.

## Compile and run

From this project folder with JDK 17 or newer:

```powershell
javac -encoding UTF-8 --release 17 -d out "@sources.txt"
java -cp out todo.App
```

The default data file is `tasks.txt`. To use a separate fictional workspace:

```powershell
java -cp out todo.App "practice-tasks.txt"
```

Every accepted mutation is saved immediately. Listing, exiting, and an incomplete command at EOF do not rewrite the data. If startup cannot parse the existing file, the application stops with a nonzero exit code; it never replaces that file with an empty list.

Menu options 1-5 retain the original add/list/complete/delete/exit order. Options 6-9 add edit, reopen, search, and reload. Search accepts `all`, `open`, or `done`. Deletion requires typing `DELETE`. The editor asks for a replacement title and description; a blank description clears it.

## Persistence and recovery

Tasks are immutable values with positive IDs, versions, validated text, and consistent completion timestamps. A service mutation constructs a candidate snapshot, saves it, then updates in-memory state. A failed save leaves both the previous accepted state and the current service view unchanged.

The versioned `TODOLIST1` format stores a snapshot revision, a durable next-ID watermark, Base64-encoded text fields, and an end count. It rejects malformed UTF-8, invalid booleans, duplicate IDs, impossible timestamps, invalid watermarks, and truncated records. Files are bounded to 8 MiB and snapshots to 10,000 tasks. IDs are never reused after deleting the highest task and restarting.

The original six-field `key=value` format is read strictly when all fields and closing separators are present. Its first successful conversion preserves the original bytes in `tasks.txt.legacy-backup` (or the equivalent sibling for a custom path). A different existing backup stops conversion. There is no silent data-repair mode: inspect malformed data separately and keep the original.

Saves coordinate participating processes through a sibling `.lock` file, compare the loaded bytes with the current file, flush a temporary sibling, and replace the target atomically. If another session has saved, the stale session receives a conflict. Choose Reload, review the accepted data, and re-enter the intended change. The application does not automatically merge or retain rejected terminal input as a draft.

## Verify

With Python 3 and JDK 17 available:

```powershell
python scripts/verify.py
```

The recorded run used Microsoft Build of OpenJDK 17.0.10 (any JDK 17+ works; install from https://learn.microsoft.com/java/openjdk/download or `winget install Microsoft.OpenJDK.17`). Set `JAVA_HOME` if the JDK is not on PATH. The helper compiles into a temporary directory and runs model, repository, service, CLI, and two-JVM checks using only temporary data. Evidence goes to `.verification`; set `TODO_VERIFY_RESULTS_DIR` to choose a different report directory. See [the verification record](astraupskill/VERIFICATION.md) for the actual results.

## Learning scope

This project remains a CLI. It has no HTTP API, browser interface, accounts, authorization, audit history, or deployed database. The course maps the existing boundaries to a future web adapter and SQL repository. Cooperative file locking does not protect against unrelated programs that ignore the lock, and atomic replacement support depends on the filesystem. The implementation deliberately fails if atomic replacement is unavailable rather than silently downgrading to a truncating write. It does not claim certified power-loss recovery or multi-machine storage.

The [historical README](docs/HISTORICAL-README.md) and original onboarding notes are preserved for comparison. Prefer the current `astraupskill` course when method names or behavior differ.
