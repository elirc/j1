# What This File Is For

`TaskRepository.java` handles persistence. It reads tasks from a local text file and writes the current task list back to that file.

This file is a repository and storage adapter.

## Why This File Matters

This file matters because it defines the boundary between in-memory objects and durable storage. If the app remembers tasks between runs, this file is why.

It also teaches a very common engineering lesson: storage code often looks simple at first, but small format choices create long-term constraints.

## Key Exports / Main Units

- `TaskRepository(String fileName)`
  Configures the storage path.
- `loadTasks()`
  Reads the file, parses task blocks, and returns task objects.
- `saveTasks(List<Task> tasks)`
  Serializes tasks to the storage format.
- `parseTask(List<String> lines)`
  Converts one block of text into one `Task`.
- `toStorageValue(LocalDateTime dateTime)`
  Converts optional timestamps into stored text.

## How It Works

The repository uses a simple custom text format:

- each field is stored as `key=value`
- each task ends with a line containing `---`

Load flow:

1. If the file does not exist, return an empty list.
2. Read the file line by line.
3. Group lines into one block per task.
4. Parse each block into a `Task`.

Save flow:

1. Open the file for writing.
2. Write each task as a block of key/value lines.
3. Separate blocks with `---`.

Important implementation detail:

- `parseTask()` treats malformed numbers or timestamps as `IOException`.
- The repository expects required fields like `id`, `title`, `completed`, and `createdAt` to be present.

## How It Connects To Other Files

Inbound relationships:

- Called by `App` on startup and shutdown.

Outbound relationships:

- Creates `Task` objects while loading.
- Reads data that `TaskManager` will later treat as the in-memory source of truth.

Important contract:

- The save format and load format must stay in sync.
- The rest of the app assumes loaded tasks are structurally valid.

## Things A Junior Dev Should Notice

- This repository is not using JSON or a database; it uses a teaching-friendly custom format.
- The format is easy to read, but it is also easier to break with unexpected input.
- Because parsing is hand-written, every new field increases maintenance cost a little.
- `Boolean.parseBoolean()` is permissive, so invalid boolean text becomes `false` instead of throwing.

## Code Review Lens

In a pull request touching this file, focus on:

- backward compatibility of saved data
- whether load and save logic still match exactly
- whether malformed data fails clearly
- whether user-entered text can break the storage format

Easy-to-miss risks:

- titles or descriptions containing newline characters
- changing a field name in one direction only
- adding a new field without deciding how older saved files should behave

## Suggested Exercises

1. Write down one example task block and explain how `parseTask()` would turn it into a `Task`.
2. Identify one weakness of the custom format and propose a simple mitigation.
3. If you added a `priority` field, list every method in this file that would need review.

## Observed Facts vs Inference

Observed from code:

- The repository stores tasks in a local text file.
- Missing files are treated as an empty task list.
- Parsing errors are wrapped as `IOException`.

Inference / likely intent:

- The author chose a deliberately simple persistence format to keep the project beginner-friendly.
- The code favors readability over robustness against every edge case.
