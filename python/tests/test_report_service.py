from datetime import datetime

from src.report_service import compute_velocity
from src.task_service import TASKS, create_task


def setup_function():
    TASKS.clear()


def test_compute_velocity_same_day_completion():
    # A task started and completed on the same day has a cycle time of 0 days.
    # Velocity should still be computable, not crash on a divide-by-zero.
    create_task(1, "Hotfix", project_id=1, priority="high")
    completed = [
        {
            "task_id": 1,
            "started_at": datetime(2026, 7, 8, 9, 0),
            "completed_at": datetime(2026, 7, 8, 17, 0),
        }
    ]
    result = compute_velocity(1, completed)
    assert result["tasks_completed"] == 1
    assert result["total_points"] == 3
