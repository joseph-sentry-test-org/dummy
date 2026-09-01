import pytest

from src.models import UserNotFoundError
from src.user_service import USERS, create_user, get_user


def setup_function():
    USERS.clear()


def test_get_user_returns_existing_user():
    create_user(1, "Ada", "Lovelace", "ada@example.com")
    user = get_user(1)
    assert user.id == 1
    assert user.first_name == "Ada"


def test_get_user_raises_user_not_found_error_for_missing_id():
    with pytest.raises(UserNotFoundError) as exc_info:
        get_user(999)
    assert exc_info.value.user_id == 999


def test_get_user_error_message_includes_user_id():
    with pytest.raises(UserNotFoundError) as exc_info:
        get_user(999)
    assert "999" in str(exc_info.value)
