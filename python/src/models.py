from dataclasses import dataclass, field


class UserNotFoundError(KeyError):
    """Raised when a user ID is not found in the user store."""

    def __init__(self, user_id: int):
        super().__init__(user_id)
        self.user_id = user_id

    def __str__(self):
        return f"User {self.user_id} not found"


@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool = True


@dataclass
class Project:
    id: int
    name: str
    owner_id: int


@dataclass
class Task:
    id: int
    title: str
    project_id: int
    assignee_id: int | None = None
    priority: str = "medium"
    status: str = "todo"
    tags: list[str] = field(default_factory=list)
