# What This File Is For

`Task.java` defines the core domain object for the application. It represents one to-do item and stores the data that the rest of the system reads and updates.

This file is a domain model.

## Why This File Matters

This file matters because every other source file depends on the shape and behavior of `Task`. If you misunderstand this file, the rest of the app will feel harder than it really is.

It also teaches a small but important idea: even a simple data object can still protect its own state transitions.

## Key Exports / Main Units

- `Task(...)` constructor
  Creates a task with all its fields.
- Getter methods
  Expose task data to the rest of the app.
- `hasDescription()`
  Convenience method for display logic.
- `markCompleted()`
  Changes a task from incomplete to completed and assigns the completion timestamp.

## How It Works

The file has a small amount of behavior around a mostly data-oriented object.

Important structure:

- `id`, `title`, `description`, and `createdAt` are set when the task is created.
- `completed` and `completedAt` can change later.

Important state transition:

- `markCompleted()` only works once.
- If the task is already completed, it returns `false`.
- If not, it sets `completed = true` and assigns `completedAt = LocalDateTime.now()`.

That is a useful design choice because it keeps the completion rule close to the data it affects.

## How It Connects To Other Files

Inbound relationships:

- Created by `TaskManager` for new tasks.
- Created by `TaskRepository` when loading from disk.

Outbound relationships:

- Read by `TaskManager` for business operations.
- Read by `App` indirectly when tasks are displayed.

Important contract:

- Other files rely on `Task` to represent completion consistently through `completed` and `completedAt`.

## Things A Junior Dev Should Notice

- The class is not fully immutable; some fields change over time.
- `description` is normalized to `""` when `null` is passed in.
- `markCompleted()` is doing more than flipping a boolean; it also protects an invariant.
- There is no general-purpose setter API, which keeps the object simpler and harder to misuse.

## Code Review Lens

In a pull request touching this file, focus on:

- whether state transitions still make sense
- whether new fields have clear ownership and lifecycle rules
- whether mutability is increasing in a controlled way
- whether timestamps remain consistent with task status

Easy-to-miss risks:

- adding setters that let outside code create inconsistent state
- allowing `completed = true` while `completedAt` stays `null`
- adding a field but forgetting how it should be loaded and saved

## Suggested Exercises

1. Explain why `markCompleted()` belongs here instead of in `App`.
2. Propose one invariant for `Task` and describe how the class currently protects it.
3. Imagine adding a priority field. Decide whether it should be mutable and why.

## Observed Facts vs Inference

Observed from code:

- `Task` stores id, title, description, completion status, and timestamps.
- `markCompleted()` returns `false` when the task is already complete.

Inference / likely intent:

- The author wants `Task` to be simple, but not just a passive bag of fields.
- The class is designed to keep a small amount of domain behavior close to the data.
