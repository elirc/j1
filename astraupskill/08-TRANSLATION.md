# 08. Port this to C#

[Course index](README.md)

Two pages, three mechanisms. Everything else in this course is language-neutral.

## 1. The `Task` value object

```csharp
public sealed record TaskItem(int Id, int Version, string Title, bool Done, DateOnly? DueDate)
{
    public TaskItem
    {
        if (Id < 0) throw new ArgumentOutOfRangeException(nameof(Id));
        if (Version < 1) throw new ArgumentOutOfRangeException(nameof(Version));
        if (string.IsNullOrWhiteSpace(Title) || Title.Length > 200) throw new ArgumentException("Title must be 1-200 characters.");
    }
    public TaskItem WithTitle(string title) => this with { Title = title };
}
```

A `record` gives what the Java class hand-writes: immutability, value equality, and a validated constructor. `with` expressions replace the copy-constructor helpers.

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
