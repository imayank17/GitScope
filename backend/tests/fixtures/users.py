import pytest

@pytest.fixture
def mock_user_data():
    """Placeholder user fixture for future authentication integration."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "testuser@gitscope.org",
        "is_active": True,
        "is_superuser": False
    }


@pytest.fixture
def mock_admin_data():
    """Placeholder admin fixture for future authentication integration."""
    return {
        "id": 2,
        "username": "admin",
        "email": "admin@gitscope.org",
        "is_active": True,
        "is_superuser": True
    }
