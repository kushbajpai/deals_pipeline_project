"""Integration tests for authentication and authorization system.

Tests user registration, login, token refresh, and role-based access control.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from deals_processor.main import app
from deals_processor.core.database import get_database_instance
from deals_processor.models.user import RoleModel

# Create test client
client = TestClient(app)


def setup_test_database() -> Session:
    """Set up test database with default roles.

    Returns:
        Session: Database session.
    """
    db_instance = get_database_instance()
    db_instance.init_db()

    db = db_instance.get_session()

    # Create default roles if they don't exist
    roles = ["admin", "analyst", "partner"]
    for role_name in roles:
        if not db.query(RoleModel).filter(RoleModel.name == role_name).first():
            role = RoleModel(
                name=role_name,
                description=f"{role_name.title()} role",
                level=100 if role_name == "admin" else 50 if role_name == "analyst" else 10,
                is_active=True,
            )
            db.add(role)
    db.commit()
    return db


def test_health_check() -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    print("✓ Health check passed")


def test_user_registration() -> None:
    """Test user registration endpoint."""
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    print("✓ User registration passed")
    return data


def test_user_login(email: str = "testuser@example.com", password: str = "SecurePassword123!") -> dict:
    """Test user login endpoint.

    Args:
        email: User email.
        password: User password.

    Returns:
        dict: Login response data.
    """
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    print("✓ User login passed")
    return data


def test_get_current_user(access_token: str) -> None:
    """Test get current user endpoint.

    Args:
        access_token: Valid access token.
    """
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data
    print("✓ Get current user passed")


def test_refresh_token(refresh_token: str) -> None:
    """Test token refresh endpoint.

    Args:
        refresh_token: Valid refresh token.
    """
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    print("✓ Token refresh passed")


def test_unauthorized_access() -> None:
    """Test unauthorized access without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401
    print("✓ Unauthorized access denied correctly")


def test_invalid_credentials() -> None:
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={"email": "invalid@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    print("✓ Invalid credentials rejected correctly")


def test_duplicate_email() -> None:
    """Test registration with duplicate email."""
    # Register first user
    response1 = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
            "full_name": "User One",
        },
    )
    assert response1.status_code == 200

    # Try to register with same email
    response2 = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
            "full_name": "User Two",
        },
    )
    assert response2.status_code == 409
    print("✓ Duplicate email rejected correctly")


def main() -> None:
    """Run all authentication tests."""
    print("\n" + "=" * 60)
    print("Authentication System Integration Tests")
    print("=" * 60 + "\n")

    try:
        # Setup
        print("[Setup] Initializing test database...")
        setup_test_database()
        print("[Setup] Test database ready\n")

        # Run tests
        print("[Tests] Running authentication tests...\n")
        test_health_check()
        test_unauthorized_access()
        test_invalid_credentials()

        registration_data = test_user_registration()
        access_token = registration_data["access_token"]
        refresh_token = registration_data["refresh_token"]

        test_get_current_user(access_token)
        test_refresh_token(refresh_token)

        login_data = test_user_login()
        test_get_current_user(login_data["access_token"])

        test_duplicate_email()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
