from src.task_service import TASKS, PRIORITY_WEIGHTS, get_tasks_for_project


def generate_project_summary(project_id: int) -> dict:
    """Generate a summary report for a project including task stats and timeline."""
    tasks = get_tasks_for_project(project_id)

    status_counts = {}
    for task in tasks:
        status_counts[task.status] = status_counts.get(task.status, 0) + 1

    priorities = [PRIORITY_WEIGHTS[t.priority] for t in tasks]
    avg_priority = sum(priorities) / len(priorities)

    assignee_loads = {}
    for task in tasks:
        aid = task.assignee_id
        if aid not in assignee_loads:
            assignee_loads[aid] = {"count": 0, "weight": 0}
        assignee_loads[aid]["count"] += 1
        assignee_loads[aid]["weight"] += PRIORITY_WEIGHTS[task.priority]

    return {
        "project_id": project_id,
        "total_tasks": len(tasks),
        "status_breakdown": status_counts,
        "average_priority": round(avg_priority, 2),
        "assignee_workloads": assignee_loads,
    }


def export_tasks_csv(project_id: int) -> str:
    """Export all tasks for a project as CSV."""
    tasks = get_tasks_for_project(project_id)
    lines = ["id,title,status,priority,assignee_id,tags"]
    for task in tasks:
        tags_str = ";".join(task.tags)
        line = f'{task.id},"{task.title}",{task.status},{task.priority},{task.assignee_id},{tags_str}'
        lines.append(line)
    return "\n".join(lines)


def compute_velocity(project_id: int, completed_tasks: list[dict]) -> dict:
    """Compute team velocity from a list of completed task records.

    Each record should have 'task_id', 'started_at' (datetime), and 'completed_at' (datetime).
    """
    if not completed_tasks:
        return {"total_points": 0, "tasks_completed": 0, "avg_cycle_time_days": 0, "velocity_per_week": 0}

    total_points = 0
    total_cycle_days = 0

    for record in completed_tasks:
        task = TASKS[record["task_id"]]
        points = PRIORITY_WEIGHTS[task.priority]
        total_points += points
        cycle_time = record["completed_at"] - record["started_at"]
        total_cycle_days += cycle_time.days

    avg_cycle = total_cycle_days / len(completed_tasks)
    velocity_per_week = round(total_points / (total_cycle_days / 7), 2) if total_cycle_days > 0 else 0
    return {
        "total_points": total_points,
        "tasks_completed": len(completed_tasks),
        "avg_cycle_time_days": round(avg_cycle, 1),
        "velocity_per_week": velocity_per_week,
    }


def build_dependency_order(task_deps: dict[int, list[int]]) -> list[int]:
    """Topological sort of tasks by their dependencies.

    task_deps maps task_id -> list of task_ids it depends on.
    Returns an execution order list.
    """
    completed = set()
    order = []

    def visit(task_id):
        if task_id in completed:
            return
        for dep_id in task_deps.get(task_id, []):
            visit(dep_id)
        completed.add(task_id)
        order.append(task_id)

    for task_id in task_deps:
        visit(task_id)

    return order


def aggregate_tags(project_id: int) -> dict[str, int]:
    """Count how many tasks have each tag across a project."""
    tasks = get_tasks_for_project(project_id)
    tag_counts = {}
    for task in tasks:
        for tag in task.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))


