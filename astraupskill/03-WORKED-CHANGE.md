# Worked change: implement an edit that can fail safely

The user story is: "I can update a task's title and description, and I can trust that a success message means the edit was saved." Add two failure criteria: an old expected version must not overwrite a newer edit, and a persistence failure must leave the previous accepted task unchanged. These criteria determine the implementation structure.

## The three methods the edit passes through

`editTask` is deliberately small: the expected version is checked first, a replacement value is built, and only `replace` reaches the durable commit. From `src/todo/service/TaskManager.java:39-51`:

```java
    private Task expected(int id, int version) {
        Task task = findTaskById(id);
        if (task.getVersion() != version) throw new IllegalStateException("Task version changed. Reload and review before retrying.");
        return task;
    }
    private Task replace(Task replacement) throws IOException {
        var tasks = new ArrayList<>(snapshot.tasks());
        tasks.replaceAll(t -> t.getId() == replacement.getId() ? replacement : t);
        commit(tasks, snapshot.nextId()); return replacement;
    }
    public synchronized Task editTask(int id, int version, String title, String description) throws IOException {
        return replace(expected(id, version).edit(title, description));
    }
```

## Capture the value being edited

In [App.java](../src/todo/App.java), option 6 obtains a task through `selected`, displays its current values, and reads the replacement title and description. The selected task is immutable, so the version and content describe a stable value. The terminal passes its ID and version to the service with the user's replacement fields (`App.java:32`).

Be precise about what this protects in the CLI. Selection and save happen within one command on one thread, so nothing in this process can change the task in between, and `expected` always matches here. When a *second terminal* has saved, this session's snapshot still shows version 1, so the version check passes. The repository's file-baseline comparison (`TaskRepository.java:50`) is what rejects the stale write. The version parameter becomes the active guard once an adapter holds a version across time, such as an HTTP client.

A future browser form would keep the same captured version in draft state. Fetching a new version automatically just before saving would defeat the purpose: it could approve an overwrite the user never reviewed. Treat the version as part of the user's editing context, not as a number to refresh until a request succeeds.

## Build a candidate without mutating accepted state

In [TaskManager](../src/todo/service/TaskManager.java), `editTask` calls `expected`. A missing task or mismatched version rejects the operation. The immutable task's `edit` method validates the new text and returns a replacement with the next version. The manager then constructs a candidate list and snapshot.

For example, suppose task 4 is version 2 with title "Study file storage." An accepted edit to "Study atomic file storage" creates task version 3 and increments the workspace revision. Its ID and creation timestamp stay the same. An attempted second edit carrying version 2 is rejected before persistence, leaving version 3 unchanged. The unit test `stale record version rejects without changing accepted data` (`TaskWorkflowTest.java:61`) does exactly this through the service API.

## Cross the durable boundary

`commit` calls [the repository](../src/todo/repository/TaskRepository.java). The repository compares the file with the baseline that this session loaded, coordinates other participating processes, and writes a complete temporary snapshot. Only an accepted atomic replacement advances the repository baseline. Only then does the manager replace its in-memory snapshot.

The test suite injects a failure immediately before replacement by overriding `replaceAtomically` in a test repository. It verifies that the original bytes remain and the manager still returns the previously accepted tasks. This is a meaningful failure test because the candidate was valid and the failure occurred at the persistence boundary.

## Explain the user recovery path

The CLI reports that the change was not accepted. A stale session can choose Reload, inspect the latest file, and re-enter its intended edit. It does not keep a separate rejected draft or perform an automatic merge. State that limitation clearly rather than implying that terminal input is recoverable after the user moves on.

Your review should show the validation rule, version check, candidate construction, commit order, and evidence. Together they explain why a small edit feature is reliable across both successful and failed writes.
