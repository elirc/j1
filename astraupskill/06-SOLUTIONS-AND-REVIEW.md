# Solution guidance and review checklist

Compare your attempted exercises with the reasoning below. The strongest solution is one whose behavior and limits another engineer can verify. Having the most abstractions or dependencies does not make a solution stronger.

## The standard your solution has to meet

Every extension still has to keep this case green: an injected failure at the commit boundary leaves both memory and the file unchanged. From `test/todo/TaskWorkflowTest.java:64`:

```java
        test("atomic replacement failure retains memory and disk", () -> { Path p=file(); manager(p).addTask("Existing task",""); byte[] before=Files.readAllBytes(p); TaskRepository failing=new TaskRepository(p.toString()) { protected void replaceAtomically(Path a,Path b)throws IOException{throw new IOException("Injected move failure");} }; TaskManager m=new TaskManager(failing,CLOCK); rejects(IOException.class,()->m.addTask("Rejected task","")); check(m.getAllTasks().size()==1&&Arrays.equals(before,Files.readAllBytes(p))); });
```

Run the suite after every exercise. Compile into a scratch directory so the repository stays clean:

```bash
javac -encoding UTF-8 --release 17 -d "$TMP/todo-classes" $(git ls-files 'src/*.java' 'test/*.java')
java -cp "$TMP/todo-classes" todo.TaskWorkflowTest "$TMP/todo-unit"   # ends with RESULT {"passed":true,"tests":35}
```

## Exercise 1: guarantees

There is nothing to implement. The value of this exercise is the prediction step. If you guessed that the stale session is caught by the task *version* check, read finding 4 below: the version check is not what stops it.

## Exercise 2: misleading failure paths

Each fix is one line, and the fix belongs where the misleading decision is made:

- **CRLF:** in `decode` (`TaskRepository.java:107`), detect `TODOLIST1\r\n` before the legacy fallback and throw an `IOException` that names line endings. Do not "helpfully" strip `\r`. Silently rewriting the file's bytes would also change the baseline comparison at line 50.
- **Id overflow:** bound the pattern in `selected` (`App.java:43`) to `[1-9][0-9]{0,8}`, or catch `NumberFormatException` there and rethrow the friendly message. Catching it in the menu loop instead would hide real programming errors.
- **Empty backup:** in `save` (`TaskRepository.java:51`), back up only a non-empty baseline (`baseline.length > 0`). An empty file has nothing to preserve.

## Exercise 3: due date

Use `LocalDate`, and keep due dates separate from `createdAt` and `completedAt`. Past dates are valid data, because an overdue task is still a real task. Compute "overdue" at display time from an injected `Clock` (the `TaskManager` constructor already accepts one at `TaskManager.java:20`), so tests do not break tomorrow.

Format: write a new header (`TODOLIST2`) with an exact 8-field row and keep the 7-field `TODOLIST1` branch strict. Also update the legacy check in `save` (`TaskRepository.java:51`). Otherwise the first save of a `TODOLIST2` file treats it as "legacy" and writes a backup on every conversion. Extend the CRLF guard from Exercise 2 to the new header as well. Once the CLI writes `TODOLIST2`, the Exercise 2 Check converts a `TODOLIST2` file and fails again until you do. This is the regression the earlier Check exists to catch.

The trap is input parsing. `LocalDate.parse("2027-02-29")` throws `DateTimeParseException`, and the CLI's catch at `App.java:37` lists only `IOException | IllegalArgumentException | IllegalStateException`. Wrap the parse and rethrow `IllegalArgumentException("Enter a real calendar date as YYYY-MM-DD.")`. The decoder already does the same conversion for stored dates at `TaskRepository.java:118`.

## Exercise 4: HTTP adapter

A good handler is a thin translator:

- Parse the id and `If-Match`, and return 428 when the header is missing.
- Call `manager.editTask(id, version, title, description)`.
- Map `IllegalStateException` to 409, "Task not found." to 404, any other `IllegalArgumentException` to 400, and `IOException` from the repository to 503.
- Put `"<new version>"` in the `ETag` header.

Two `IllegalArgumentException` cases share a type here. Distinguishing 404 from 400 by message text works, but it is brittle. A mid-level refactor gives the service a dedicated `TaskNotFoundException`.

The version check that is useless inside the CLI (finding 4) is exactly what makes this endpoint safe. A browser draft holds version 1 for minutes while other clients edit. Do not "fix" a 409 by re-fetching the version and retrying. That approves an overwrite the user never reviewed.

## Exercise 5: SQL rules

Keep the allocation watermark in a one-row `meta` table, or use `AUTOINCREMENT`, which also never reuses ids. Do not use `MAX(id) + 1`, which reuses the id of a deleted highest task. Read and bump the watermark in the same transaction as the `INSERT`.

For edits, run one `UPDATE ... WHERE id = ? AND version = ?`. If `changes === 0`, issue a follow-up `SELECT` to tell `missing` from `stale`. A `CHECK (length(trim(title)) BETWEEN 1 AND 160)` constraint protects rows written by anything, including a future migration script. It does not decide who may edit a task, and it does not tell the user what to do after a stale result.

## Senior findings in the delivered code

These were reproduced on 2026-10-06 against the delivered source (JDK 17.0.10, scratch copy, fictional files). None of them loses accepted data. Findings 1-3 are diagnosis defects, and findings 4-5 are design facts that a reviewer should be able to state.

1. **A CRLF-converted snapshot is misdiagnosed as a broken legacy file.** `decode` sends any text not starting with exactly `TODOLIST1\n` to the legacy parser (`TaskRepository.java:107`). That parser splits on `\r?\n` and rejects the `TODOLIST1` line as a field without `=` (`TaskRepository.java:126`). Opening the file in an editor that converts it to CRLF produces `Startup stopped; existing data was not replaced. Unknown, duplicate or malformed legacy field.` with exit code 1. The data is safe, but the message sends the user to the wrong format. The source files themselves are committed with CRLF endings, which makes this mistake easy to make on Windows.
2. **An oversized id leaks a Java parse message.** `selected` accepts any digit string (`App.java:43`), and `Integer.parseInt("99999999999")` throws `NumberFormatException`. That exception is a subclass of `IllegalArgumentException`, so the menu's catch (`App.java:37`) prints `Change not accepted: For input string: "99999999999"`. It is handled, but by accident.
3. **An empty existing file gets an empty `.legacy-backup`.** `legacy("")` returns an empty snapshot (`TaskRepository.java:121`). The non-null, zero-byte baseline then fails the `TODOLIST1` prefix test in `save` (`TaskRepository.java:51`) and is "preserved" as a 0-byte backup (line 53). That backup then blocks any later legacy conversion to the same path with "A different legacy backup exists."
4. **Inside the CLI, the task version check can never fail.** Options 3, 4, 6 and 7 read the task and pass its own `getVersion()` within a single command on one thread (`App.java:30-32`), so `TaskManager.expected` (`TaskManager.java:39-43`) always matches. In the two-terminal conflict, both sessions see version 1 of their own snapshot. The *file baseline* comparison (`TaskRepository.java:50`) rejects the stale one. The version check exists for adapters that hold a version across time, such as an HTTP client (Exercise 4). The unit test at `TaskWorkflowTest.java:61` exercises it by calling the service directly.
5. **The baseline is a whole-file optimistic lock.** Any accepted save by another session makes every later mutation in this session fail, even one that touches an unrelated task. `TaskWorkflowTest.java:62` shows this with two different new tasks. That is safe and simple, but under real concurrency it produces false conflicts. A SQL store with per-row versions (Exercise 5) conflicts only when two writers touch the same task.
6. **Good design worth naming: two locks, on purpose.** `FileChannel.lock()` coordinates processes, but a second lock attempt on the same file from the *same* JVM throws `OverlappingFileLockException` rather than waiting. The static `LOCAL_LOCKS` map (`TaskRepository.java:18`) serializes same-JVM callers before the file lock is taken (line 47). That keeps two `TaskManager`s in one test process from crashing each other.

## Before requesting review

State the trigger, the accepted result, the rejected result, and your evidence: which Check, and which line of output. Include at least one failure test, and describe what remains unproven. For example, a local SQL prototype proves the conditional-update rule. It does not prove migration, deployment readiness, or power-loss recovery.
