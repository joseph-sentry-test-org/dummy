from src.models import Task

TASKS: dict[int, Task] = {}

VALID_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["in_review", "todo"],
    "in_review": ["done", "in_progress"],
    "done": [],
}

PRIORITY_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 5,
}


def create_task(
    id: int,
    title: str,
    project_id: int,
    assignee_id: int | None = None,
    priority: str = "medium",
) -> Task:
    task = Task(
        id=id, title=title, project_id=project_id, assignee_id=assignee_id, priority=priority
    )
    TASKS[id] = task
    return task


def get_task(task_id: int) -> Task:
    return TASKS[task_id]


def transition_task(task_id: int, new_status: str) -> Task:
    task = TASKS[task_id]
    allowed = VALID_TRANSITIONS[task.status]
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{task.status}' to '{new_status}'. Allowed: {allowed}"
        )
    task.status = new_status
    return task


def get_tasks_for_project(project_id: int) -> list[Task]:
    return [t for t in TASKS.values() if t.project_id == project_id]


def get_highest_priority_task(project_id: int) -> Task:
    project_tasks = get_tasks_for_project(project_id)
    return max(project_tasks, key=lambda t: PRIORITY_WEIGHTS[t.priority])


def bulk_reassign(from_user_id: int, to_user_id: int, project_id: int) -> list[Task]:
    """Reassign all tasks from one user to another within a project."""
    from src.user_service import USERS

    target_user = USERS[to_user_id]
    if not target_user.is_active:
        raise ValueError(f"Cannot assign to inactive user {to_user_id}")

    reassigned = []
    project_tasks = get_tasks_for_project(project_id)
    for task in project_tasks:
        if task.assignee_id == from_user_id:
            if task.status == "done":
                raise ValueError(
                    f"Cannot reassign completed task {task.id} ('{task.title}')"
                )
            task.assignee_id = to_user_id
            reassigned.append(task)
    return reassigned


def batch_transition(task_ids: list[int], new_status: str) -> list[Task]:
    """Transition multiple tasks to a new status."""
    results = []
    for task_id in task_ids:
        task = transition_task(task_id, new_status)
        results.append(task)
    return results


def merge_duplicate_tasks(keep_id: int, duplicate_ids: list[int]) -> Task:
    """Merge duplicate tasks into one, combining tags and removing duplicates."""
    keep_task = TASKS[keep_id]
    for dup_id in duplicate_ids:
        dup_task = TASKS[dup_id]
        for tag in dup_task.tags:
            if tag not in keep_task.tags:
                keep_task.tags.append(tag)
        if PRIORITY_WEIGHTS[dup_task.priority] > PRIORITY_WEIGHTS[keep_task.priority]:
            keep_task.priority = dup_task.priority
        del TASKS[dup_id]
    return keep_task


def compute_project_workload(project_id: int) -> dict:
    project_tasks = get_tasks_for_project(project_id)
    total_weight = sum(PRIORITY_WEIGHTS[t.priority] for t in project_tasks)
    active = [t for t in project_tasks if t.status != "done"]
    active_weight = sum(PRIORITY_WEIGHTS[t.priority] for t in active)
    return {
        "total_tasks": len(project_tasks),
        "active_tasks": len(active),
        "completion_pct": round((total_weight - active_weight) / total_weight * 100, 1),
    }
