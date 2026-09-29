# Codebase map and reading order

Begin with [Task.java](../src/todo/model/Task.java). A task is an immutable value containing an ID, version, title, description, completion state, and timestamps. Its constructor rejects invalid combinations. `edit` and `withCompletion` return replacement values; they do not alter an object already held by another caller. This makes a returned task safe to inspect without granting hidden mutation access.

Read [TaskSnapshot](../src/todo/repository/TaskSnapshot.java) next. It represents the entire accepted workspace: a revision, a next-ID watermark, and an immutable list of tasks. The watermark must be greater than every current task ID. Keeping it separately from the maximum existing ID prevents reuse after the highest task is deleted. The constructor also rejects duplicate IDs and excessive task counts.

[TaskManager](../src/todo/service/TaskManager.java) owns the accepted in-memory snapshot. Its constructor loads through the repository. A mutation validates the target and expected task version, constructs a candidate list, and passes a new snapshot to `commit`. That method saves first and assigns `snapshot = candidate` only after the repository returns successfully. Keep this ordering in mind while reading every operation.

The [repository](../src/todo/repository/TaskRepository.java) owns the file boundary. `load` reads bounded bytes, strictly decodes them, and remembers the accepted baseline. `save` validates the next revision and watermark, obtains a cooperative file lock, compares the baseline with the current bytes, writes and flushes a temporary sibling, then replaces the target atomically. The retained `.lock` file is a coordination object; do not delete it while participating processes are running.

Finally read [App.java](../src/todo/App.java). It handles prompts, menu choices, confirmation, and user-facing failures. It captures a task before asking for edited values and passes that task's version to the service. It does not serialize records or mutate task fields itself. EOF before a command is complete exits without applying that command, while previously accepted changes are already durable.

## Trace these boundaries

For create, follow terminal text to `addTask`, the task constructor, candidate snapshot creation, repository save, and the success message. For edit, add the target lookup and expected-version comparison. For reload, notice that parsing must succeed before either the repository baseline or manager snapshot is replaced. A malformed new file therefore does not silently become an empty accepted workspace.

[TaskWorkflowTest](../test/todo/TaskWorkflowTest.java) exercises the model, store, and service. [verify.py](../scripts/verify.py) compiles the Java files and adds real CLI and two-JVM scenarios. These layers matter: an isolated model test cannot prove that the terminal correctly cancels deletion or that two separate processes coordinate their saves.

The historical onboarding notes describe the original four-class starter. They remain useful for comparing responsibilities, but the current snapshot type, immutable methods, and save-before-memory behavior supersede the earlier mutable and save-on-exit examples.
