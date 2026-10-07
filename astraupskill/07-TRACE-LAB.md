# Trace lab: accepted state, stale state, and failed state

Use a new fictional file and keep two terminal windows available. This lab is designed to make the persistence contract visible before you map it onto an HTTP request or browser form. Record the command, task version, snapshot revision, observed message, and durable result for each experiment.

## The durable boundary Trace C stops at

Trace C ends inside `save`. Note the order: revision and watermark checks, then the file lock, then the baseline byte comparison that produces the "changed in another session" message you will see in the second terminal. From `src/todo/repository/TaskRepository.java:39-50`:

```java
    public synchronized void save(TaskSnapshot candidate) throws IOException {
        if (!loaded) throw new IOException("Load the repository before saving.");
        if (current.revision() == Long.MAX_VALUE || candidate.revision() != current.revision() + 1)
            throw new IOException("Snapshot revision must advance exactly once.");
        if (candidate.nextId() < current.nextId()) throw new IOException("Next-id watermark cannot move backward.");
        byte[] encoded = encode(candidate);
        Files.createDirectories(filePath.getParent());
        Path lockPath = filePath.resolveSibling(filePath.getFileName() + ".lock");
        synchronized (LOCAL_LOCKS.computeIfAbsent(lockPath, ignored -> new Object())) {
            if (Files.isSymbolicLink(lockPath)) throw new IOException("Symbolic-link locks are unsupported.");
            try (FileChannel channel = FileChannel.open(lockPath, CREATE, WRITE); var lock = channel.lock()) {
                if (!Arrays.equals(baseline, bytes())) throw new IOException("File changed in another session. Reload before retrying; no data was overwritten.");
```

## Trace A: an accepted edit

Create a task called "Study snapshot storage" with a short description. List it and note its ID and version. Edit the title, then exit and restart. The new title should remain and the task version should have advanced. The ID and creation timestamp should stay stable.

Trace the call in [App.java](../src/todo/App.java), then [TaskManager](../src/todo/service/TaskManager.java). Locate the immutable replacement task and the candidate snapshot. In [TaskRepository](../src/todo/repository/TaskRepository.java), identify the byte comparison, temporary write, flush, and atomic replacement. State the point after which the manager is allowed to show the candidate as accepted state.

## Trace B: a stale session

Start both terminal windows against the same file before making another change. In the first, create a task and wait for its success message. In the second, try creating a different task. The second session's candidate is based on its older baseline and should be rejected. List tasks in that second session and explain why it still shows its previously accepted in-memory snapshot.

Choose Reload in the second session. Inspect the task accepted by the first, then deliberately re-enter the second task. Confirm that both now appear after restart and have distinct IDs. Explain why the lock alone would not have been sufficient without comparing the baseline. Both processes can take the lock successfully at different times while still holding different historical reads.

## Trace C: a failed persistence boundary

Read the injected-move-failure test rather than damaging a normal file. The test creates valid candidate data and fails immediately before replacement. Its assertions compare both durable bytes and the manager's list. Write down what would go wrong if the manager assigned the candidate before calling `repository.save`.

Now inspect the malformed-startup CLI check. The program must stop without creating an empty replacement, even when it could otherwise continue displaying a menu. Explain the difference between a genuinely absent new file and an existing unreadable file. Treating those states as equivalent is a data-loss bug.

## Transfer the reasoning to the web

Sketch a browser edit carrying a captured version. Map the terminal's conflict message to a controlled HTTP conflict response and a retained browser draft. Map the repository commit to a database transaction. Then list what is missing from the CLI: authentication, ownership, browser recovery, request bounds, and transport tests. These are future implementation requirements, not features already present.

Finish with a short review using [the verification evidence](VERIFICATION.md): one guarantee you proved, one implementation decision you can explain, and one limitation you would address next. This makes the lab a demonstration of engineering judgment rather than a checklist of menu options.
