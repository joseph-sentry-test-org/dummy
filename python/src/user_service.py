from src.models import User

USERS: dict[int, User] = {}


class UserNotFoundError(Exception):
    """Raised when a user with the given ID does not exist."""


def create_user(id: int, first_name: str, last_name: str, email: str) -> User:
    user = User(id=id, first_name=first_name, last_name=last_name, email=email)
    USERS[id] = user
    return user


def get_user(user_id: int) -> User:
    if user_id not in USERS:
        raise UserNotFoundError(f"User {user_id} not found")
    return USERS[user_id]


def get_display_name(user: User) -> str:
    return user.first_name.strip() + " " + user.last_name.strip()


def format_user_email(user: User) -> str:
    name, domain = user.email.split("@")
    return f"{name} ({domain})"


def deactivate_user(user_id: int) -> User:
    user = USERS[user_id]
    user.is_active = False
    return user


def get_active_users() -> list[User]:
    return [u for u in USERS.values() if u.is_active]


def find_user_by_email(email: str) -> User | None:
    for user in USERS.values():
        if user.email == email:
            return user
    return None


def batch_create_users(user_data: list[dict]) -> list[User]:
    """Create multiple users from a list of dicts. Each dict needs id, first_name, last_name, email."""
    created = []
    for data in user_data:
        user = create_user(data["id"], data["first_name"], data["last_name"], data["email"])
        created.append(user)
    return created
