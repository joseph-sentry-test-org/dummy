from src.models import Task
from src.notification_service import notify_task_assignees, send_notification
from src.task_service import TASKS
from src.user_service import USERS, create_user


def setup_function():
    USERS.clear()
    TASKS.clear()


def test_send_notification_to_existing_user():
    create_user(1, "Ada", "Lovelace", "ada@example.com")
    result = send_notification(1, "Hello {{recipient_name}}!", {})
    assert result["status"] == "sent"
    assert result["to"] == "ada@example.com"


def test_notify_task_assignees_handles_missing_user():
    # Task assigned to a user that no longer exists. Mirrors the production
    # AttributeError — sending a notification must not crash on a missing
    # assignee; the task should be skipped instead.
    TASKS[1] = Task(id=1, title="Ship it", project_id=1, assignee_id=999)
    results = notify_task_assignees([1], "Hi {{recipient_name}}", {})
    assert results == []


def test_send_notification_raises_for_missing_user():
    # send_notification should raise ValueError when the user_id doesn't exist,
    # not a cryptic KeyError or AttributeError.
    import pytest
    with pytest.raises(ValueError, match="User 999 not found"):
        send_notification(999, "Hello!", {})
