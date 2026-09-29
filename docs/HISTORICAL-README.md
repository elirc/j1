# Historical description of the original implementation

The current code and setup are documented in the root README and learning course (folder `astraupskill`). The original load fallback, mutable model, save-on-exit behavior, and storage methods below are superseded.

# CLI To-Do Manager

This is a small Java command-line project built for learning. It uses plain Java, basic object-oriented design, and a simple text file for persistence so you can understand the whole project without needing frameworks or advanced tools.

## Project Overview

The app lets a user manage tasks from the terminal.

- Add a task
- List all tasks
- Mark a task as completed
- Delete a task
- Save tasks to disk
- Load tasks from disk when the program starts

The code is intentionally small and split into only a few classes so each class has one clear job.

## Folder Structure

```text
J1/
├── README.md
└── src/
    └── todo/
        ├── App.java
        ├── model/
        │   └── Task.java
        ├── repository/
        │   └── TaskRepository.java
        └── service/
            └── TaskManager.java
```

## How To Compile And Run

From the project root:

```powershell
javac -d out src/todo/App.java src/todo/model/Task.java src/todo/service/TaskManager.java src/todo/repository/TaskRepository.java
java -cp out todo.App
```

When the program runs, it creates a `tasks.txt` file in the project folder when it saves data.

## File-By-File Explanation

### `src/todo/App.java`

This is the entry point. It handles:

- starting the program
- showing the menu
- reading user input
- calling the correct business logic
- saving on exit

It does not store tasks directly. It asks `TaskManager` and `TaskRepository` to do that work.

### `src/todo/model/Task.java`

This is the data model. A `Task` object represents one to-do item.

It stores:

- `id`
- `title`
- `description`
- `completed`
- `createdAt`
- `completedAt`

### `src/todo/service/TaskManager.java`

This is the business logic class. It manages the in-memory list of tasks.

It knows how to:

- add tasks
- complete tasks
- delete tasks
- calculate the next unique id
- format tasks for display

### `src/todo/repository/TaskRepository.java`

This handles file reading and file writing.

It knows how to:

- load tasks from `tasks.txt`
- convert file text into `Task` objects
- save `Task` objects back into the file

This separation is useful because file storage and task logic are different responsibilities.

## Class-By-Class Explanation

### `App`

Think of this class as the program coordinator.

- It owns the `Scanner` for reading terminal input.
- It owns a `TaskManager` for task operations.
- It owns a `TaskRepository` for saving and loading.

`App` is mostly about interaction with the user.

### `Task`

Think of this class as a blueprint for one task.

- It holds the task's data.
- It exposes getters so other classes can read the data safely.
- It has `markCompleted()` so the task can update its own completion state.

### `TaskManager`

Think of this class as the rules layer.

- It stores tasks in a list while the app is running.
- It creates new tasks with new ids.
- It finds tasks by id.
- It decides what happens when a task is completed or deleted.

### `TaskRepository`

Think of this class as the storage layer.

- It reads from the disk.
- It writes to the disk.
- It converts between file text and Java objects.

## Method-By-Method Explanation

### `App`

`main`
- Creates the repository.
- Creates the app.
- Starts the program.

`run`
- Loads tasks.
- Starts the menu loop.
- Saves tasks when the loop ends.

`loadTasksFromDisk`
- Reads tasks from the repository.
- Passes them into the manager.
- Falls back to an empty list if loading fails.

`saveTasksToDisk`
- Asks the repository to write all tasks to disk.

`printMenu`
- Prints the numbered menu options.

`addTask`
- Reads title and description from the user.
- Calls `taskManager.addTask(...)`.

`listTasks`
- Gets all tasks from the manager.
- Prints each task in a readable format.

`completeTask`
- Reads an id from the user.
- Asks the manager to mark that task complete.

`deleteTask`
- Reads an id from the user.
- Asks the manager to delete that task.

`readRequiredLine`
- Keeps asking until the user enters non-empty text.

`readTaskId`
- Reads text and tries to turn it into an integer.
- Returns `-1` if the input is invalid.

### `Task`

Constructor
- Builds a task object with all fields.

Getter methods
- Return the values stored in the task.

`hasDescription`
- Returns `true` if the description is not blank.

`markCompleted`
- Changes `completed` to `true`.
- Sets `completedAt` to the current time.
- Returns `false` if the task was already completed.

### `TaskManager`

Constructor
- Creates the internal task list.
- Sets `nextId` to `1`.

`loadTasks`
- Replaces the current in-memory tasks with loaded tasks.
- Sorts them by id.
- Recalculates the next id.

`addTask`
- Creates a new `Task`.
- Uses `nextId` so ids stay unique.
- Adds the task to the list.

`getAllTasks`
- Returns a copy of the task list.

`completeTask`
- Finds a task by id.
- Calls `markCompleted()` on it.

`deleteTask`
- Finds a task by id.
- Removes it from the list.

`formatTaskForDisplay`
- Builds the text shown in the terminal when listing tasks.

`findTaskById`
- Loops through tasks and returns the matching one.

`calculateNextId`
- Finds the highest existing id and returns one more than that.

`formatDate`
- Converts a `LocalDateTime` into a cleaner display string.

### `TaskRepository`

Constructor
- Stores the path to the data file.

`loadTasks`
- Returns an empty list if the file does not exist.
- Reads the file block by block.
- Converts each block into a `Task`.

`saveTasks`
- Writes every task into the file in plain text form.

`parseTask`
- Reads one saved task block.
- Extracts each field.
- Creates a `Task` object.

`toStorageValue`
- Converts a date to text.
- Returns an empty string if the date is `null`.

## Data Flow Explanation

The data moves through the program like this:

1. The app starts.
2. `App` asks `TaskRepository` to load tasks from `tasks.txt`.
3. `TaskRepository` creates `Task` objects from the file.
4. `App` gives those tasks to `TaskManager`.
5. The user chooses menu options.
6. `App` reads the choice and calls methods on `TaskManager`.
7. `TaskManager` changes the in-memory list of tasks.
8. When the app exits, `App` asks `TaskRepository` to save the current task list.

## How Saving And Loading Works

The project uses a simple custom text format instead of JSON or CSV.

Example:

```text
id=1
title=Buy milk
description=From the grocery store
completed=true
createdAt=2026-03-26T14:30:00
completedAt=2026-03-26T14:45:00
---
```

Why use this format?

- It is easy to read with your own eyes.
- It is easy to write using plain Java.
- It avoids needing a JSON library.
- It avoids complicated CSV edge cases.

Tradeoff:

- JSON is more common in real projects.
- But JSON without an external library would make this beginner project more complicated.

So this format is not the most standard, but it is very teachable.

## How The Menu Loop Works

The menu loop is in `App.run()`.

- A `boolean running = true` variable controls the loop.
- While `running` is `true`, the menu is shown again and again.
- The user enters a choice.
- A `switch` statement decides which method to call.
- If the user enters `5`, `running` becomes `false`.
- The loop ends, and the app saves tasks before closing.

This pattern is very common in command-line programs.

## Why The Project Was Structured This Way

The structure is small, but each class has one main responsibility:

- `App` handles user interaction
- `Task` represents data
- `TaskManager` handles business logic
- `TaskRepository` handles persistence

This is a beginner-friendly version of separation of concerns.

Benefits:

- Each file is shorter and easier to read
- Changes are safer because code is organized by responsibility
- You can study one idea at a time
- The `main` method stays simple

## What A Beginner Should Study First

Study in this order:

1. `Task.java`
2. `TaskManager.java`
3. `App.java`
4. `TaskRepository.java`

Why this order?

- `Task` is the easiest class and teaches the data model first.
- `TaskManager` shows how objects are used together.
- `App` shows how user input connects to the logic.
- `TaskRepository` is slightly more advanced because it uses file I/O.

Important Java topics to focus on:

- classes and objects
- constructors
- fields and methods
- lists
- loops
- conditionals
- `switch`
- `LocalDateTime`
- file reading and writing

## 3 Small Exercises To Extend The Project

1. Add an edit feature.
   Let the user change a task title or description by id.

2. Add a filter for incomplete tasks only.
   Create a menu option that shows only tasks that are not completed.

3. Add task search.
   Let the user type a keyword and list only tasks whose title or description contains that keyword.
