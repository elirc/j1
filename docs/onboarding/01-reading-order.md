# Reading Order

## Why This Reading Order

This project is small, so the goal is not to memorize every file. The goal is to build a mental model in the right order:

1. understand the data
2. understand the rules
3. understand the program flow
4. understand persistence

That order makes the later files much easier to read.

## Stage 1: Start With The Domain Model

Read:

- `src/todo/model/Task.java`

Why this comes first:

- It is the smallest file.
- It defines the core object that everything else works with.
- It introduces the key state transitions, especially completion.

Try to learn:

- what data a task holds
- which fields are mutable vs fixed
- what the code considers a valid completion state

Checkpoint:

- After this stage, you should understand what one task looks like in memory.

## Stage 2: Read The Business Logic

Read:

- `src/todo/service/TaskManager.java`

Why this comes next:

- Once you understand `Task`, you can follow how the app creates, updates, and deletes tasks.
- This file shows the main rules of the system without the distraction of terminal I/O or file parsing.

Try to learn:

- where ids come from
- how tasks are found and updated
- which logic belongs in the manager instead of in `App`

Checkpoint:

- After this stage, you should understand the main operations of the app and the basic invariants around ids and completion.

## Stage 3: Read The Entry Point And Menu Flow

Read:

- `src/todo/App.java`

Why this comes after the manager:

- `App` makes more sense once you already know what operations it is calling.
- This file teaches how a CLI loop coordinates the rest of the system.

Try to learn:

- how the menu loop works
- where input validation happens
- how the app handles startup and shutdown

Checkpoint:

- After this stage, you should understand how a user action turns into a business operation.

## Stage 4: Read Persistence Last

Read:

- `src/todo/repository/TaskRepository.java`

Why this comes last:

- It is the most implementation-sensitive file.
- It mixes file I/O, parsing, and error handling, which is easier once the rest of the system is already familiar.

Try to learn:

- how tasks are serialized to text
- how text becomes `Task` objects again
- what assumptions the format makes

Checkpoint:

- After this stage, you should understand the full path from startup load to exit save.

## Tracing Exercises

1. Trace "add task" from the menu option in `App` to the new `Task` instance in `TaskManager`.
2. Trace "complete task" from user input to the moment `completedAt` is assigned.
3. Trace startup from `main()` through loading the task file and into the manager.
4. Trace shutdown from choosing "Exit" to writing `tasks.txt`.

## What To Notice While Reading

- Which decisions are about user experience and which are about business rules.
- Which data is stored only while the app is running and which data must survive restarts.
- Which parts of the code would need to change together if a new task field were added.

## Good Follow-Up Questions

- If we added "edit task," which class should own the change?
- If we changed the file format, which invariants would we need to preserve?
- If this project grew larger, which file would likely need to be split first?
