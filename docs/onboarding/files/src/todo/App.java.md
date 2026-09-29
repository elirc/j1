# What This File Is For

`App.java` is the application entry point and CLI coordinator. It is responsible for starting the program, loading saved tasks, running the menu loop, reading user input, and saving tasks when the program exits.

This file is best understood as an entry point and interaction layer, not as the place where core business rules should live.

## Why This File Matters

This file matters because it shows the app's main execution flow. If you want to understand what happens from program startup to shutdown, this is the file to trace.

It also teaches a useful design habit: the entry point should coordinate work, not own every decision itself.

## Key Exports / Main Units

- `main(String[] args)`
  Creates the repository, creates the app instance, and starts the program.
- `run()`
  Loads tasks, runs the menu loop, and ensures tasks are saved on exit.
- `addTask()`
  Collects user input and delegates task creation.
- `listTasks()`
  Fetches tasks and prints them in a readable format.
- `completeTask()`
  Reads an id and delegates completion.
- `deleteTask()`
  Reads an id and delegates deletion.
- `loadTasksFromDisk()`
  Handles startup loading and fallback behavior.
- `saveTasksToDisk()`
  Handles persistence during shutdown.

## How It Works

The main control flow is:

1. `main()` builds a `TaskRepository` and an `App`.
2. `run()` loads tasks from disk.
3. `run()` enters a `while (running)` menu loop.
4. The user enters a menu choice.
5. A `switch` dispatches to one of the action methods.
6. On exit, the `finally` block saves tasks and closes the scanner.

Important detail:

- The `finally` block means the app tries to save even if something goes wrong during the loop.

This file also owns input validation at the CLI boundary:

- `readRequiredLine()` rejects blank required text.
- `readTaskId()` handles non-numeric ids without crashing.

## How It Connects To Other Files

Inbound relationships:

- The JVM starts execution here through `main()`.

Outbound relationships:

- Calls `TaskRepository.loadTasks()` and `TaskRepository.saveTasks()`.
- Calls `TaskManager.loadTasks()`, `addTask()`, `getAllTasks()`, `completeTask()`, `deleteTask()`, and `formatTaskForDisplay()`.
- Works with `Task` objects returned from the manager.

Important contract:

- `App` assumes `TaskManager` owns task rules and `TaskRepository` owns storage details.

## Things A Junior Dev Should Notice

- This file does not directly manipulate the task list.
- The menu loop is simple because the app is small, but this file could grow too quickly if many new features are added.
- Input validation here is about user interaction, not deep domain validation.
- Saving happens on exit, not after every command.

## Code Review Lens

In a pull request touching this file, focus on:

- whether business logic is staying out of the CLI layer
- whether bad input is still handled gracefully
- whether startup and shutdown behavior remain reliable
- whether new menu options keep the file readable

Easy-to-miss risks:

- adding a feature that bypasses save/load expectations
- inconsistent handling of invalid ids across commands
- growing `App` into a "god class"

## Suggested Exercises

1. Trace what happens when the user enters `3` and then types an invalid id.
2. Add a new menu option on paper first, and decide which part should live in `App` versus `TaskManager`.
3. Identify one spot where a future refactor might split `App` into smaller helpers.

## Observed Facts vs Inference

Observed from code:

- `App` creates `TaskRepository` directly.
- `App` owns the `Scanner`.
- `App` loads before the menu loop and saves in a `finally` block.

Inference / likely intent:

- The author wants startup and shutdown behavior to be hard to forget.
- The design favors explicit coordination over more abstract patterns like dependency injection.
