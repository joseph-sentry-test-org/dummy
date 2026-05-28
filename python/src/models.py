from dataclasses import dataclass, field


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
