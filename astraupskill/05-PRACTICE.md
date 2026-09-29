# Practice: take the next step toward a CRUD web service

These exercises build on the existing guarantees rather than replacing the small project wholesale. Work in a separate branch or copy and use fictional task files. Before implementing an exercise, write a concrete acceptance example and identify which existing behavior must continue to hold.

## Exercise 1: add a due date

Add an optional calendar due date to a task and allow the author of a local command to edit or clear it. Decide whether past dates are allowed and how overdue status is displayed. A due date is a calendar date, not an instant; do not introduce a time zone conversion merely to render it. Keep creation and completion timestamps separate from this new field.

Version the storage format deliberately. Old snapshots should still load through an explicit decoder, while newly written snapshots preserve the due date. Test absent dates, leap days, invalid calendar values, a cleared date, and a failed save. The acceptance example should include restart: "After editing a due date and restarting, the same calendar date is shown." Do not call a compile-only check proof of persistence.

## Exercise 2: add a rejected-edit export

The CLI currently requires re-entering a rejected change after a stale-file conflict. Add an explicit export of the user's attempted title, description, task ID, and captured version. The export should create a new file without overwriting an existing one. It should not alter the task store, silently retry the mutation, or refresh the captured version.

Test cancellation, a destination that already exists, and a failed export. Explain how a user compares the exported edit with the current task after Reload. Consider whether the export contains private task text before sharing it as a debugging artifact. Import and automatic merge are separate product decisions, not implicit consequences of adding export.

## Exercise 3: design a narrow HTTP adapter

Sketch endpoints for list, create, edit, completion state, and delete. Use strict request DTOs containing only editable fields and an expected version where needed. Map missing tasks, invalid input, stale versions, and storage failures to distinct responses. Do not expose arbitrary filesystem paths in request parameters. The server should choose its configured storage location.

Implement the adapter only after defining authentication and ownership for a web context. A localhost CLI's lack of accounts is not an authorization design. Test requests directly against the HTTP boundary and add browser draft behavior if you build a UI. Keep the existing immutable model and service invariants; a route handler should not mutate task fields or serialize snapshots independently.

## Exercise 4: replace file snapshots with SQL

Introduce a repository implementation backed by a local relational database. Preserve stable IDs, record versions, atomic mutations, and failure semantics. Decide whether the allocation watermark belongs in a sequence or metadata row. Use a conditional update with the expected task version, and distinguish a missing record from a stale one.

Plan a validated migration into a new database with a dry-run count report. Keep the original file and its legacy backup unchanged. Reuse the service behavior tests where possible, then add database-specific constraint and transaction tests. Your review should explain which guarantees moved from application code into database constraints and which still require service policy.
