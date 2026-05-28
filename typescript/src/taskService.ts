import type { Task } from "./models.js";

const tasks = new Map<number, Task>();

const VALID_TRANSITIONS: Record<string, string[]> = {
  todo: ["in_progress"],
  in_progress: ["in_review", "todo"],
  in_review: ["done", "in_progress"],
  done: [],
};

const PRIORITY_WEIGHTS: Record<string, number> = {
  low: 1,
  medium: 2,
  high: 3,
  critical: 5,
};

export function createTask(
  id: number,
  title: string,
  projectId: number,
  assigneeId: number | null = null,
  priority: Task["priority"] = "medium"
): Task {
  const task: Task = {
    id,
    title,
    projectId,
    assigneeId,
    priority,
    status: "todo",
    tags: [],
  };
  tasks.set(id, task);
  return task;
}

export function getTask(taskId: number): Task {
  return tasks.get(taskId)!;
}

export function transitionTask(taskId: number, newStatus: string): Task {
  const task = tasks.get(taskId)!;
  const allowed = VALID_TRANSITIONS[task.status];
  if (!allowed.includes(newStatus)) {
    throw new Error(
      `Cannot transition from '${task.status}' to '${newStatus}'. Allowed: ${allowed}`
    );
  }
  task.status = newStatus as Task["status"];
  return task;
}

export function getTasksForProject(projectId: number): Task[] {
  return [...tasks.values()].filter((t) => t.projectId === projectId);
}

export function getHighestPriorityTask(projectId: number): Task {
  const projectTasks = getTasksForProject(projectId);
  return projectTasks.reduce((highest, task) =>
    PRIORITY_WEIGHTS[task.priority] > PRIORITY_WEIGHTS[highest.priority] ? task : highest
  );
}

export function bulkReassign(fromUserId: number, toUserId: number, projectId: number): Task[] {
  const projectTasks = getTasksForProject(projectId);
  const reassigned: Task[] = [];
  for (const task of projectTasks) {
    if (task.assigneeId === fromUserId) {
      if (task.status === "done") {
        throw new Error(`Cannot reassign completed task ${task.id} ('${task.title}')`);
      }
      task.assigneeId = toUserId;
      reassigned.push(task);
    }
  }
  return reassigned;
}

export function mergeDuplicateTasks(keepId: number, duplicateIds: number[]): Task {
  const keepTask = tasks.get(keepId)!;
  for (const dupId of duplicateIds) {
    const dupTask = tasks.get(dupId)!;
    for (const tag of dupTask.tags) {
      if (!keepTask.tags.includes(tag)) {
        keepTask.tags.push(tag);
      }
    }
    if (PRIORITY_WEIGHTS[dupTask.priority] > PRIORITY_WEIGHTS[keepTask.priority]) {
      keepTask.priority = dupTask.priority;
    }
    tasks.delete(dupId);
  }
  return keepTask;
}

export function computeProjectWorkload(projectId: number): Record<string, number> {
  const projectTasks = getTasksForProject(projectId);
  const totalWeight = projectTasks.reduce((sum, t) => sum + PRIORITY_WEIGHTS[t.priority], 0);
  const active = projectTasks.filter((t) => t.status !== "done");
  const activeWeight = active.reduce((sum, t) => sum + PRIORITY_WEIGHTS[t.priority], 0);
  return {
    totalTasks: projectTasks.length,
    activeTasks: active.length,
    completionPct: Math.round(((totalWeight - activeWeight) / totalWeight) * 1000) / 10,
  };
}
