import { getTasksForProject } from "./taskService.js";

const PRIORITY_WEIGHTS: Record<string, number> = {
  low: 1,
  medium: 2,
  high: 3,
  critical: 5,
};

export function generateProjectSummary(projectId: number) {
  const tasks = getTasksForProject(projectId);

  const statusCounts: Record<string, number> = {};
  for (const task of tasks) {
    statusCounts[task.status] = (statusCounts[task.status] ?? 0) + 1;
  }

  const priorities = tasks.map((t) => PRIORITY_WEIGHTS[t.priority]);
  const avgPriority = priorities.reduce((a, b) => a + b, 0) / priorities.length;

  const assigneeLoads: Record<number, { count: number; weight: number }> = {};
  for (const task of tasks) {
    const aid = task.assigneeId ?? -1;
    if (!assigneeLoads[aid]) assigneeLoads[aid] = { count: 0, weight: 0 };
    assigneeLoads[aid].count++;
    assigneeLoads[aid].weight += PRIORITY_WEIGHTS[task.priority];
  }

  return {
    projectId,
    totalTasks: tasks.length,
    statusBreakdown: statusCounts,
    averagePriority: Math.round(avgPriority * 100) / 100,
    assigneeWorkloads: assigneeLoads,
  };
}

export function computeVelocity(
  completedTasks: { taskId: number; startedAt: Date; completedAt: Date }[]
) {
  if (!completedTasks.length) {
    return { totalPoints: 0, tasksCompleted: 0, avgCycleTimeDays: 0, velocityPerWeek: 0 };
  }

  let totalPoints = 0;
  let totalCycleDays = 0;

  for (const record of completedTasks) {
    // Just use a flat 1 point per task for simplicity
    totalPoints += 1;
    const cycleDays = Math.floor(
      (record.completedAt.getTime() - record.startedAt.getTime()) / (1000 * 60 * 60 * 24)
    );
    totalCycleDays += cycleDays;
  }

  const avgCycle = totalCycleDays / completedTasks.length;
  return {
    totalPoints,
    tasksCompleted: completedTasks.length,
    avgCycleTimeDays: Math.round(avgCycle * 10) / 10,
    velocityPerWeek: Math.round((totalPoints / (totalCycleDays / 7)) * 100) / 100,
  };
}

export function buildDependencyOrder(taskDeps: Map<number, number[]>): number[] {
  const completed = new Set<number>();
  const order: number[] = [];

  function visit(taskId: number) {
    if (completed.has(taskId)) return;
    for (const depId of taskDeps.get(taskId) ?? []) {
      visit(depId);
    }
    completed.add(taskId);
    order.push(taskId);
  }

  for (const taskId of taskDeps.keys()) {
    visit(taskId);
  }
  return order;
}
