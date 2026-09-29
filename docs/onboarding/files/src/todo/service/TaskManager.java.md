# What This File Is For

`TaskManager.java` is the business logic layer for the application. It manages the in-memory list of tasks and owns the main operations the app supports.

This file is a domain service.

## Why This File Matters

This file matters because it contains the core rules of the app:

- how new tasks are created
- how ids are assigned
- how tasks are found
- how completion and deletion work

If you want to understand the app's behavior without the noise of terminal input or file parsing, this is the best file to study.

## Key Exports / Main Units

- `loadTasks(List<Task> loadedTasks)`
  Replaces the current in-memory state with loaded tasks and recalculates the next id.
- `addTask(String title, String description)`
  Creates and stores a new task.
- `getAllTasks()`
  Returns a copy of the current task list.
- `completeTask(int taskId)`
  Finds a task and marks it complete.
- `deleteTask(int taskId)`
  Removes a task by id.
- `formatTaskForDisplay(Task task)`
  Builds a readable CLI representation of a task.

## How It Works

This class owns two pieces of state:

- the current `List<Task>`
- `nextId`, which is used for new task creation

Key control flow:

- On startup, `loadTasks()` clears the current list, loads saved tasks, sorts them by id, and recalculates `nextId`.
- On add, `addTask()` creates a new `Task` using the current `nextId`, stores it, then increments `nextId`.
- On complete or delete, the manager first finds the task by id, then performs the operation if the task exists.

Important design detail:

- `getAllTasks()` returns a new list instead of the internal list itself.

That reduces accidental external modification of the manager's collection, even though the `Task` objects inside are still mutable.

## How It Connects To Other Files

Inbound relationships:

- Called by `App` for all user-triggered operations.

Outbound relationships:

- Creates and updates `Task` objects.
- Formats timestamps for CLI display.

Important contract:

- `TaskManager` assumes the repository can provide a valid list of `Task` objects.
- `App` assumes the manager is the source of truth for in-memory task behavior.

## Things A Junior Dev Should Notice

- This class mixes domain logic and display formatting. That is acceptable in a tiny CLI app, but it may be a refactor point later.
- `nextId` is derived from loaded data, which preserves id stability across restarts.
- Deleting a task does not reduce `nextId` or reuse ids.
- `findTaskById()` is a linear search, which is fine for a small project.

## Code Review Lens

In a pull request touching this file, focus on:

- whether ids remain stable and unique
- whether task state transitions remain valid
- whether behavior on missing ids is still correct
- whether display formatting changes accidentally hide important information

Easy-to-miss risks:

- reusing ids after deletion
- returning direct access to internal state
- moving too much presentation logic into the service as the app grows

## Suggested Exercises

1. Trace how `nextId` is computed after loading tasks with ids `2`, `5`, and `9`.
2. Identify one reason `getAllTasks()` returns a copy of the list.
3. Propose how you would add "list only incomplete tasks" without making `App` smarter than it should be.

## Observed Facts vs Inference

Observed from code:

- `TaskManager` stores tasks in an `ArrayList`.
- It uses the highest existing id plus one for new task ids.
- It uses `Task.markCompleted()` instead of setting completion fields itself.

Inference / likely intent:

- The author wants one place to own the app's rules.
- The code is optimized for readability over scalability.
