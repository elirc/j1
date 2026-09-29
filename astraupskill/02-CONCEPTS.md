# Concepts that transfer to CRUD web development

## Immutable values protect the service boundary

Returning a new list does not protect a manager if the list contains the same mutable task objects it owns. A caller could retrieve a task and change its completion state without validation or persistence. The current [Task](../src/todo/model/Task.java) is immutable. An edit returns a new value with an incremented version. The service decides whether that replacement becomes accepted state.

This resembles using read DTOs and explicit commands in a web application. A GET response should not imply that the client may replace every field on a database entity. Editable title and description belong in an update command; identity and creation time remain controlled by the application.

## Validation is more than checking for empty text

A valid task has a positive ID and version, bounded control-free text, and a creation time within the supported range. A completed task requires a completion timestamp no earlier than creation; an open task must not retain a completion timestamp. Reopening clears that timestamp deliberately. These rules should hold for newly entered tasks and loaded data alike.

The storage decoder treats types as untrusted input. It rejects unknown or duplicate legacy fields, invalid booleans, duplicate task IDs, malformed UTF-8, and missing record terminators. Silently treating an invalid boolean as false would invent a state the file did not actually represent. In a web API, the equivalent mistake is accepting malformed JSON fields through permissive coercion.

## Atomic replacement and stale-write detection solve different problems

Writing a complete temporary file and atomically replacing the target prevents a normal reader from observing half a new snapshot. It does not tell you whether your candidate was based on an old read. Two sessions could both write complete files while the later one erases the earlier one's change.

The repository therefore holds a cooperative file lock and compares the loaded baseline with the current bytes before replacement. A stale session fails and asks the user to reload. Within a manager, expected task versions also prevent applying an edit to a value that has already changed. A future SQL implementation would use a transaction plus an expected-version update predicate rather than assuming transactions alone preserve user intent.

## Commit before reporting success

The manager creates a candidate without replacing its accepted state. If encoding, backup protection, locking, or atomic replacement fails, the old accepted snapshot remains visible. The terminal prints a success message only after persistence returns. This ordering prevents a common inconsistency where the screen says a task exists but a restart loses it.

## Identity is historical, not positional

A task ID is not its position in a list, and the next ID is not simply the current maximum plus one after every restart. The snapshot retains the allocation watermark even after deletion. That avoids reusing a deleted identity, which becomes especially important when future URLs, logs, or related records refer to a task. Explain this before replacing the IDs with a different scheme merely because it looks more modern.

## Glossary

*Value object*: an immutable, validated object compared by contents (`Task`; a C# `record`). *Baseline*: the file contents last read, compared before an overwrite. *Stale write*: a change based on an old baseline. *Atomic replacement*: write to a temp file, then rename over the original. *Commit before report*: only say "saved" after the durable write returned. *Historical identity*: an id is never reused or renumbered when positions change. *Concurrency token*: the C# equivalent of the baseline (see 08).

