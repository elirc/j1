# 08. Port this to C#

[Course index](README.md)

Two pages, three mechanisms. Everything else in this course is language-neutral.

## 1. The `Task` value object

```csharp
public sealed record TaskItem
{
    public int Id { get; }
    public int Version { get; }
    public string Title { get; }
    public string Description { get; }

    public TaskItem(int id, int version, string title, string? description)
    {
        if (id < 1 || version < 1) throw new ArgumentException("Positive id and version required.");
        Title = Text(title, 1, 160, "Title");
        Description = Text(description ?? "", 0, 2000, "Description");
        Id = id; Version = version;
    }

    static string Text(string value, int min, int max, string label)
    {
        var s = value.Trim();
        if (s.Length < min || s.Length > max || s.Any(char.IsControl))
            throw new ArgumentException($"{label} must contain {min}..{max} characters without controls.");
        return s;
    }

    // Mirrors Task.edit (Task.java:42): new value, next version, validation re-run.
    public TaskItem Edit(string title, string? description) =>
        new(Id, checked(Version + 1), title, description);
}
```

Completion state and the timestamps are left out to keep this short. Add them the same way. A `record` gives you value equality, and get-only properties give you immutability. Two Java-to-C# traps are worth knowing:

- **C# has no compact constructor.** Java's `public TaskSnapshot { ... }` validation block (`TaskSnapshot.java:6`) has no C# equivalent. A positional record `record TaskItem(int Id, ...)` cannot validate its parameters in a constructor body, so this example uses an explicit constructor.
- **`with` skips your constructor.** `item with { Title = "" }` copies the object and sets the property directly, so no validation runs and `Version` is not bumped. That is why the properties have no `init` accessor (so `with` cannot set them) and edits go through `Edit`, just as Java callers must use `edit`/`withCompletion`. `checked` turns version overflow into an exception, like `nextVersion` at `Task.java:38-41`.

## 2. The version check

```csharp
public sealed class TaskRow
{
    public int Id { get; set; }
    [ConcurrencyCheck] public int Version { get; set; }   // or [Timestamp] public byte[] RowVersion
    public string Title { get; set; } = "";
    public bool Done { get; set; }
}

// service
var row = await db.Tasks.SingleAsync(t => t.Id == id);
if (row.Version != expectedVersion) throw new StaleEditException(row.Version);
row.Title = title; row.Version++;
try { await db.SaveChangesAsync(); }                      // UPDATE ... WHERE Id = @p0 AND Version = @p1
catch (DbUpdateConcurrencyException) { throw new StaleEditException(); }
```

EF Core turns `[ConcurrencyCheck]` into the `WHERE Version = @expected` predicate the Java course simulates with the file baseline; zero affected rows becomes the exception you map to 409.

## 3. The file baseline as a conditional update

Where the Java repository compares the bytes it last read before rewriting the file, the SQL version is one statement:

```sql
UPDATE Tasks SET Title = @title, Version = Version + 1 WHERE Id = @id AND Version = @expected;
-- rows affected: 1 = accepted, 0 = stale edit
```

Commit-before-report survives unchanged: return the new version only after `SaveChangesAsync` (the commit) has returned.

## Exercise

Write the two-context test: load task 1 in `dbA` and `dbB`, save a title change through `dbA`, then through `dbB`, and assert `DbUpdateConcurrencyException` on the second. Then write the HTTP version with `If-Match: "1"` and a 428 when the header is missing.
