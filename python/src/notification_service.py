from src.user_service import USERS


def _render_template(template: str, context: dict) -> str:
    """Replace {{key}} placeholders in a template string."""
    result = template
    for key, value in context.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def send_notification(user_id: int, template: str, context: dict) -> dict:
    """Send a notification to a user by rendering a template."""
    missing_user = USERS.get(user_id)
    if missing_user is None:
        raise ValueError(f"User {user_id} not found")
    ctx = {**context, "recipient_name": missing_user.first_name + " " + missing_user.last_name, "email": missing_user.email}
    body = _render_template(template, ctx)
    return {"to": missing_user.email, "body": body, "status": "sent"}


def notify_task_assignees(task_ids: list[int], template: str, context: dict) -> list[dict]:
    """Send notifications to all assignees of the given tasks."""
    from src.task_service import TASKS

    results = []
    for task_id in task_ids:
        task = TASKS[task_id]
        if task.assignee_id is not None and task.assignee_id in USERS:
            result = send_notification(task.assignee_id, template, context)
            results.append(result)
    return results


def send_digest(user_id: int, items: list[dict]) -> dict:
    """Build and send a daily digest email summarizing activity."""
    user = USERS[user_id]
    lines = [f"Hi {user.first_name},", "", "Here's your daily digest:", ""]
    for item in items:
        timestamp = item["timestamp"].strftime("%H:%M")
        lines.append(f"  [{timestamp}] {item['action']}: {item['target']}")
    lines.append("")
    lines.append(f"Total activity: {len(items)} events")
    body = "\n".join(lines)
    return {"to": user.email, "body": body, "status": "sent"}
