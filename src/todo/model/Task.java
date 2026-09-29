package todo.model;

import java.time.LocalDateTime;
import java.util.Objects;

/** Immutable task value. Changes return a new version instead of leaking mutable state. */
public final class Task {
    private final int id, version;
    private final String title, description;
    private final boolean completed;
    private final LocalDateTime createdAt, completedAt;

    public Task(int id, String title, String description, boolean completed,
                LocalDateTime createdAt, LocalDateTime completedAt) {
        this(id, 1, title, description, completed, createdAt, completedAt);
    }
    public Task(int id, int version, String title, String description, boolean completed,
                LocalDateTime createdAt, LocalDateTime completedAt) {
        if (id < 1 || version < 1) throw new IllegalArgumentException("Positive id and version required.");
        this.id = id; this.version = version;
        this.title = text(title, 1, 160, "Title");
        this.description = text(description == null ? "" : description, 0, 2000, "Description");
        this.createdAt = Objects.requireNonNull(createdAt, "Creation time required.");
        if (createdAt.getYear() < 1970 || createdAt.getYear() > 2100)
            throw new IllegalArgumentException("Creation year must be 1970..2100.");
        if (completed != (completedAt != null) || (completedAt != null &&
                (completedAt.isBefore(createdAt) || completedAt.getYear() > 2100)))
            throw new IllegalArgumentException("Completion time must match state and follow creation.");
        this.completed = completed; this.completedAt = completedAt;
    }
    private static String text(String value, int min, int max, String label) {
        if (value == null) throw new IllegalArgumentException(label + " is required.");
        String result = value.strip();
        if (result.length() < min || result.length() > max || result.chars().anyMatch(Character::isISOControl))
            throw new IllegalArgumentException(label + " must contain " + min + ".." + max + " characters without controls.");
        return result;
    }
    private int nextVersion() {
        if (version == Integer.MAX_VALUE) throw new IllegalStateException("Task version exhausted.");
        return version + 1;
    }
    public Task edit(String title, String description) {
        return new Task(id, nextVersion(), title, description, completed, createdAt, completedAt);
    }
    public Task withCompletion(boolean value, LocalDateTime at) {
        if (value == completed) return this;
        return new Task(id, nextVersion(), title, description, value, createdAt, value ? at : null);
    }
    public int getId() { return id; }
    public int getVersion() { return version; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public boolean isCompleted() { return completed; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getCompletedAt() { return completedAt; }
    public boolean hasDescription() { return !description.isBlank(); }
}
