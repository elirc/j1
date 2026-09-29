# Codebase Map

## What Kind Of Application This Is

This repository contains a small Java command-line application for managing to-do tasks. A user interacts with the program through a text menu in the terminal, and task data is persisted to a local text file between runs.

For a junior developer, this is a good example of a small application with clear separation of concerns:

- one file for user interaction
- one file for the domain model
- one file for business logic
- one file for persistence

## Main Architectural Layers

Observed from code:

- `src/todo/App.java` is the entry point and CLI interaction layer.
- `src/todo/model/Task.java` is the domain model.
- `src/todo/service/TaskManager.java` is the in-memory business logic layer.
- `src/todo/repository/TaskRepository.java` is the persistence layer.

Likely intent:

- keep `main` thin
- keep file I/O away from user interaction logic
- make the task rules easy to change without rewriting the CLI

## Major Runtime Boundaries

In this repo, the main runtime boundaries are simple but real:

- Terminal I/O: reading menu choices and printing output
- In-memory domain state: the current list of tasks while the app is running
- File persistence: reading from and writing to `tasks.txt`
- Time boundary: timestamps are created at runtime using `LocalDateTime.now()`

There are no network calls, databases, background jobs, or auth systems in this project.

## Important Directories

- `src/todo/`
  Owns the main application entry point.
- `src/todo/model/`
  Owns the core domain object, `Task`.
- `src/todo/service/`
  Owns business operations on tasks.
- `src/todo/repository/`
  Owns storage and parsing logic.
- `docs/onboarding/`
  Owns the onboarding material you are reading now.

## How Data Flows Through The App

The main flow is:

1. The application starts in `App.main()`.
2. `App.run()` loads tasks from `TaskRepository`.
3. Loaded `Task` objects are passed into `TaskManager`.
4. The menu loop reads the user's choice from the terminal.
5. `App` calls the matching `TaskManager` method.
6. `TaskManager` updates the in-memory task list or a `Task` object.
7. When the program exits, `App` asks `TaskRepository` to save the latest list to disk.

This is a useful pattern to notice:

- input and output stay in `App`
- rules stay in `TaskManager`
- state lives in `Task` objects and the manager's task list
- persistence stays in `TaskRepository`

## Key Concepts And Invariants

Observed from code:

- Task ids are intended to be stable and unique.
- `TaskManager` calculates the next id from the highest loaded id.
- A task can only move from incomplete to completed once through `markCompleted()`.
- `completedAt` is optional and should only be set when a task is completed.
- Missing `tasks.txt` is treated as a normal startup case, not an error.

Inference / likely intent:

- The project values simple coordination over abstraction.
- Each class is meant to own one kind of decision.

Important invariants to keep in mind:

- `title` should not be blank for valid tasks.
- `completedAt` should stay `null` for incomplete tasks.
- Deleting a task should remove it permanently from the next saved file.
- Ids should not be reused just because a task was deleted.

## Where A Junior Dev Should Be Careful

- Do not put business rules directly into `App` just because it is easy to reach from the menu loop.
- Be careful when changing the save format in `TaskRepository`; loading and saving must stay compatible.
- Remember that `TaskRepository` uses a line-based custom format, so values with embedded newlines would be risky.
- Be careful with state consistency between `completed` and `completedAt`.
- If you add new fields to `Task`, you will likely need to update both the repository and display logic.

## Complexity And Risk Hotspots

For a small project, the main hotspots are not huge, but they are worth noticing:

- `TaskRepository` is the most format-sensitive file.
  A small change in parsing or serialization can break saved data.
- `App` coordinates multiple responsibilities.
  It is easy for this file to become too large if new features are added casually.
- `TaskManager` owns id generation.
  If creation rules change, id stability needs to stay intact.

## Selected Files For Study

This repo only has four non-trivial source files, and all four were selected for onboarding:

- `src/todo/App.java`
- `src/todo/model/Task.java`
- `src/todo/service/TaskManager.java`
- `src/todo/repository/TaskRepository.java`

That is more than the suggested percentage would be in a larger repo, but it is appropriate here because each file owns a core part of the application's behavior.
