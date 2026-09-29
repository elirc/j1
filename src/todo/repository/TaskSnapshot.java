package todo.repository;
import java.util.HashSet;
import java.util.List;
import todo.model.Task;
public record TaskSnapshot(long revision, long nextId, List<Task> tasks) {
    public TaskSnapshot {
        tasks = List.copyOf(tasks);
        if (revision < 0 || nextId < 1 || nextId > (long)Integer.MAX_VALUE + 1 || tasks.size() > 10000)
            throw new IllegalArgumentException("Invalid snapshot revision, next id or capacity.");
        var ids = new HashSet<Integer>();
        for (Task task : tasks) if (!ids.add(task.getId()) || task.getId() >= nextId)
            throw new IllegalArgumentException("Duplicate task id or invalid next-id watermark.");
    }
    public static TaskSnapshot empty() { return new TaskSnapshot(0, 1, List.of()); }
}
