# Solution guidance and review checklist

Compare your attempted exercises with the reasoning below. The strongest solution is one whose behavior and limits another engineer can verify, rather than one with the most abstractions or dependencies.

## The standard your solution has to meet

Every extension discussed here still has to keep this case green: an injected failure at the commit boundary leaves both memory and the file unchanged. From `test/todo/TaskWorkflowTest.java:64`:

```java
        test("atomic replacement failure retains memory and disk", () -> { Path p=file(); manager(p).addTask("Existing task",""); byte[] before=Files.readAllBytes(p); TaskRepository failing=new TaskRepository(p.toString()) { protected void replaceAtomically(Path a,Path b)throws IOException{throw new IOException("Injected move failure");} }; TaskManager m=new TaskManager(failing,CLOCK); rejects(IOException.class,()->m.addTask("Rejected task","")); check(m.getAllTasks().size()==1&&Arrays.equals(before,Files.readAllBytes(p))); });
```

## Calendar dates need a clear product rule

For the due-date exercise, use a date type and document whether dates before today are valid. An overdue task may be useful data rather than invalid input. Validate the calendar representation and supported range, then compute overdue state for display using an injected clock or explicit comparison date. Avoid tests that become wrong tomorrow because they call the actual system date unpredictably.

A storage change requires a format decision. A new decoder should identify the new header and validate its exact field count. The old decoder should remain strict for the old format. Silently accepting extra columns in every format makes it harder to detect corruption and harder to explain what an older reader can safely load. Test conversion and restart, not just the new constructor.

## Rejected input should remain an attempted command

An export should identify the task and the version the user edited. It should not claim to be an accepted task snapshot. A new, exclusive destination prevents the export feature from overwriting an unrelated file. If export fails, report that failure separately from the earlier mutation conflict so the user understands which operation succeeded.

Do not implement recovery by automatically reloading the task and applying the exported fields with the new version. That turns stale text into an unreviewed overwrite. Show the user the accepted current record and let them decide how to reconcile the attempted change. The lack of automatic merge is acceptable when it is explicit and the data remains available.

## HTTP responses should reflect domain outcomes

A route adapter should parse a narrow request, obtain authenticated identity, call a policy-aware service, and translate expected outcomes. A missing task and a stale task are not the same failure. Neither is an invalid title equivalent to a filesystem outage. Returning success with an error string inside the body would make both the browser and monitoring harder to reason about.

The current manager has no ownership model. A web extension must add that deliberately rather than treating an ID supplied by the client as permission. Explain where the current actor comes from and where task ownership is checked. Preserve the service's save-before-memory ordering or replace it with an equivalent database commit boundary.

## SQL does not eliminate application judgment

A foreign key, unique constraint, or sequence can protect structural rules, but it does not decide whether a user may edit a task or whether a stale browser draft should overwrite current content. Keep an expected-version predicate in the update and inspect the affected-row count. Use a transaction when related records must commit together.

Before requesting review, state the trigger, accepted result, rejected result, and evidence. Include one meaningful failure test and describe remaining limitations. For example, a local SQL migration may establish rollback behavior without proving deployment readiness or power-loss recovery. Honest boundaries make the review useful and demonstrate the judgment expected of a mid-level engineer.
