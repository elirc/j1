# Practice: take the next step toward a CRUD web service

Each exercise has a **Goal** and a **Check**. Work in a branch or copy. Every Check is a dependency-free `node --test` file: it compiles your `src/` into a temporary directory and drives the real `todo.App` (or your new class) through stdin. Fictional data only, always in a temp folder. You need Node 22+ and a JDK 17+ `javac`/`java` on PATH.

## Setup: the shared harness

Create `practice/harness.mjs` in your working copy. Every test file below imports it.

```js
// practice/harness.mjs — compiles src/ once into a temp dir and drives the real CLI.
import { execFileSync, spawn, spawnSync } from 'node:child_process';
import { mkdtempSync, readdirSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

export const ROOT = resolve(process.env.TODO_ROOT ?? '.');
const walk = (d) => readdirSync(d).flatMap((n) => {
  const p = join(d, n);
  return statSync(p).isDirectory() ? walk(p) : p.endsWith('.java') ? [p] : [];
});
export const work = mkdtempSync(join(tmpdir(), 'todo-practice-'));
export const classes = join(work, 'classes');
execFileSync('javac', ['-encoding', 'UTF-8', '--release', '17', '-d', classes, ...walk(join(ROOT, 'src'))]);

/** Run the CLI to completion with the given stdin. */
export function cli(file, input) {
  const r = spawnSync('java', ['-cp', classes, 'todo.App', file], { input, encoding: 'utf8' });
  return { code: r.status, out: r.stdout, err: r.stderr };
}

/** Start a CLI session that has loaded the file but has not been sent any commands yet. */
export async function openSession(file) {
  const child = spawn('java', ['-cp', classes, 'todo.App', file]);
  let out = '';
  child.stdout.setEncoding('utf8');
  await new Promise((ok) => child.stdout.on('data', (c) => { out += c; if (out.includes('Choose: ')) ok(); }));
  return {
    finish: (input) => new Promise((ok) => {
      child.on('close', (code) => ok({ code, out }));
      child.stdin.end(input);
    }),
  };
}

/** Menu input that adds one task. Exercise 3 adds a due-date prompt: append '\n' (blank due date) here. */
export const ADD = (title) => `1\n${title}\n\n`;
```

Run one Check with `node --test practice/guarantees.test.mjs`, or all of them with `node --test --test-concurrency=1 "practice/*.test.mjs"`. Node 22 treats `node --test practice/` as a file name and fails, so use the glob. Each file compiles the project once (several seconds), and every `cli` call starts a JVM. Expect a run to take a minute or more.

## Exercise 1: pin the guarantees you already have

**Goal:** before changing anything, prove three guarantees from the README with the real CLI. A cancelled delete leaves the file byte-for-byte unchanged. A session that loaded before another session saved gets a conflict, and Reload recovers. An unreadable file stops startup without being replaced.

**Check:** `practice/guarantees.test.mjs`. This passes on the delivered code. Keep it green through every later exercise.

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { ADD, cli, openSession, work } from './harness.mjs';

test('cancelled delete leaves the file byte-for-byte unchanged', () => {
  const f = join(work, 'cancel.txt');
  cli(f, ADD('Keep me') + '5\n');
  const before = readFileSync(f);
  const r = cli(f, '4\n1\nno\n5\n');
  assert.match(r.out, /Deletion cancelled/);
  assert.deepEqual(readFileSync(f), before);
});

test('a session that loaded before another save is rejected, then Reload recovers', async () => {
  const f = join(work, 'stale.txt');
  const stale = await openSession(f);               // loads the (missing) file now
  assert.match(cli(f, ADD('First writer') + '5\n').out, /Task 1 added and saved/);
  const r = await stale.finish(ADD('Second writer') + '9\n' + ADD('Second writer') + '2\n5\n');
  assert.match(r.out, /Change not accepted: File changed in another session/);
  assert.match(r.out, /Task 2 added and saved/);    // after Reload the id watermark is current
  assert.match(cli(f, '2\n5\n').out, /First writer[\s\S]*Second writer/);
});

test('an unreadable file stops startup and is not replaced', () => {
  const f = join(work, 'bad.txt');
  writeFileSync(f, 'not a task file');
  const r = cli(f, '5\n');
  assert.equal(r.code, 1);
  assert.match(r.err, /existing data was not replaced/);
  assert.equal(readFileSync(f, 'utf8'), 'not a task file');
});
```

Before you run it, predict which line of code produces each asserted message. The answers are `App.java:31`, `TaskRepository.java:50`, and `App.java:17`.

## Exercise 2: fix three misleading failure paths

**Goal:** fix the three defects described in [findings 1-3 of the review guide](06-SOLUTIONS-AND-REVIEW.md#senior-findings-in-the-delivered-code). Each one is safe for data but confusing for users:

- A `TODOLIST1` file saved with CRLF line endings should be rejected with a message that mentions line endings. Today it reports a malformed legacy field.
- A task id too large for an `int` should get the normal "Enter a positive task id." message. Today it shows Java's `For input string`.
- An empty existing file should not leave an empty `.legacy-backup` behind on the first save.

**Check:** `practice/diagnostics.test.mjs`. All three tests fail on the delivered code. Each needs a change of about one line. Exercise 1 must stay green.

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { ADD, cli, work } from './harness.mjs';

test('a TODOLIST1 file saved with CRLF endings is diagnosed as such, not as a legacy file', () => {
  const f = join(work, 'crlf.txt');
  cli(f, ADD('A task') + '5\n');
  writeFileSync(f, readFileSync(f, 'utf8').replace(/\n/g, '\r\n'));
  const before = readFileSync(f);
  const r = cli(f, '2\n5\n');
  assert.equal(r.code, 1);
  assert.match(r.err, /line ending|CRLF/i);
  assert.deepEqual(readFileSync(f), before);
});

test('an id too large for an int gets the same message as any invalid id', () => {
  const r = cli(join(work, 'ids.txt'), '4\n99999999999\n5\n');
  assert.match(r.out, /Change not accepted: Enter a positive task id\./);
  assert.doesNotMatch(r.out, /For input string/);
});

test('an empty existing file does not leave an empty .legacy-backup behind', () => {
  const f = join(work, 'empty.txt');
  writeFileSync(f, '');
  assert.match(cli(f, ADD('First') + '5\n').out, /added and saved/);
  assert.throws(() => readFileSync(f + '.legacy-backup'), { code: 'ENOENT' });
});
```

## Exercise 3: add a due date

**Goal:** add an optional calendar due date (`java.time.LocalDate`, not an instant). Option 1 asks `Due date (YYYY-MM-DD, blank for none): ` after the description. The list shows `    Due: <date>` for tasks that have one. Choose a new header such as `TODOLIST2` for the new on-disk format, and keep the `TODOLIST1` decoder strict so existing files still load. An impossible date must be rejected without writing anything.

When this works, change `ADD` in the harness to `` `1\n${title}\n\n\n` `` so Exercises 1, 2 and 4 send a blank due date.

**Check:** `practice/due-date.test.mjs`. It fails on the delivered code: the extra input line is read as a menu choice.

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { ADD, cli, work } from './harness.mjs';

test('a leap-day due date survives a restart', () => {
  const f = join(work, 'due.txt');
  assert.match(cli(f, '1\nFile taxes\n\n2028-02-29\n5\n').out, /Task 1 added and saved/);
  assert.match(cli(f, '2\n5\n').out, /Due: 2028-02-29/);
});

test('an impossible date is rejected and nothing is written', () => {
  const f = join(work, 'bad-due.txt');
  cli(f, ADD('Existing') + '5\n');
  const before = readFileSync(f);
  assert.match(cli(f, '1\nNope\n\n2027-02-29\n5\n').out, /Change not accepted/);
  assert.deepEqual(readFileSync(f), before);
});
```

There is a trap in the second test. `LocalDate.parse` throws `DateTimeParseException`, which is a `DateTimeException` and not an `IllegalArgumentException`. The CLI's catch at `App.java:37` does not handle it, so an unwrapped parse crashes the whole session. See the review guide.

## Exercise 4: an HTTP edit endpoint with optimistic concurrency

**Goal:** add `todo.HttpApp`, a second adapter that uses the JDK's built-in `com.sun.net.httpserver` (no dependencies). Start it with `java -cp <classes> todo.HttpApp <tasks-file> <port>`. It prints `LISTENING` when ready and binds to `127.0.0.1` only. Implement `PATCH /tasks/{id}` with a form body (`title=...&description=...`) and an `If-Match: "<version>"` header. Return `428` without the header, `200` plus `ETag: "<new version>"` on success, `409` for a stale version, `404` for an unknown id, and `400` for an invalid title. The handler calls `TaskManager.editTask`. It never touches the file or the `Task` fields itself.

**Check:** `practice/http.test.mjs`. It fails on the delivered code because `HttpApp` does not exist.

```js
import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { join } from 'node:path';
import { ADD, cli, classes, work } from './harness.mjs';
// Contract: java -cp <classes> todo.HttpApp <tasks-file> <port> prints LISTENING when ready.
// PATCH /tasks/{id} with form body title=...&description=... and If-Match: "<version>".

const file = join(work, 'http.txt');
cli(file, ADD('From the CLI') + '5\n');                    // task 1, version 1
const port = 18000 + Math.floor(Math.random() * 1000);
const server = spawn('java', ['-cp', classes, 'todo.HttpApp', file, String(port)]);
after(() => server.kill());
await new Promise((ok, fail) => {
  server.stdout.on('data', (c) => String(c).includes('LISTENING') && ok());
  server.on('exit', (code) => fail(new Error('HttpApp exited with ' + code)));
});
const patch = (id, headers, title) => fetch(`http://127.0.0.1:${port}/tasks/${id}`, {
  method: 'PATCH', headers: { 'content-type': 'application/x-www-form-urlencoded', ...headers },
  body: new URLSearchParams({ title }),
});

test('missing If-Match is 428, not a blind overwrite', async () => {
  assert.equal((await patch(1, {}, 'No precondition')).status, 428);
});
test('current version is 200 with the next ETag', async () => {
  const r = await patch(1, { 'if-match': '"1"' }, 'Edited over HTTP');
  assert.equal(r.status, 200);
  assert.equal(r.headers.get('etag'), '"2"');
});
test('replaying the old version is 409 and changes nothing', async () => {
  assert.equal((await patch(1, { 'if-match': '"1"' }, 'Stale')).status, 409);
  assert.match(cli(file, '2\n5\n').out, /ID 1 \/ v2 - Edited over HTTP/);
});
test('unknown id is 404 and a blank title is 400', async () => {
  assert.equal((await patch(42, { 'if-match': '"1"' }, 'Ghost')).status, 404);
  assert.equal((await patch(1, { 'if-match': '"2"' }, '   ')).status, 400);
});
```

This endpoint has no authentication or ownership, which is why it binds to loopback only. Before it listens on any other interface, you must decide who the caller is and which tasks they own.

## Exercise 5: prototype the SQL repository's rules

**Goal:** before you replace the file store with a database, prove that the rules survive the move. Write `practice/sql-store.mjs` on Node's built-in `node:sqlite`. It exports `openStore(path)`, which returns `{ db, addTask(title), getTask(id), editTask(id, expectedVersion, title), deleteTask(id, expectedVersion) }`. Ids come from a stored watermark, never from `MAX(id) + 1`. An edit is a single `UPDATE ... WHERE id = ? AND version = ?`. Zero changed rows is then split into `missing` and `stale`. A `CHECK` constraint enforces the 1-160 character title rule in the database itself.

**Check:** `practice/sql-store.test.mjs`. It fails until `sql-store.mjs` exists. Node 22 prints an `ExperimentalWarning` for `node:sqlite`, which is expected.

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { openStore } from './sql-store.mjs';   // you write this file

test('ids come from a watermark and are never reused after deleting the highest', () => {
  const s = openStore(':memory:');
  const a = s.addTask('First');
  s.deleteTask(a.id, a.version);
  assert.equal(s.addTask('Second').id, a.id + 1);
});

test('edit with the current version wins exactly once', () => {
  const s = openStore(':memory:');
  const t = s.addTask('Draft');
  assert.deepEqual(s.editTask(t.id, 1, 'Accepted'), { status: 'ok', version: 2 });
  assert.deepEqual(s.editTask(t.id, 1, 'Stale'), { status: 'stale' });
  assert.equal(s.getTask(t.id).title, 'Accepted');
});

test('missing and stale are different outcomes', () => {
  const s = openStore(':memory:');
  assert.deepEqual(s.editTask(999, 1, 'Ghost'), { status: 'missing' });
});

test('the database itself rejects an invalid title (CHECK constraint), not just JS', () => {
  const s = openStore(':memory:');
  assert.throws(() => s.db.prepare("INSERT INTO tasks (id, version, title) VALUES (50, 1, '')").run());
});
```

In your write-up, list which guarantees moved into the database (unique ids, the title check, the atomic conditional update) and which still need application policy (who may edit, and what to show the user on `stale`).
