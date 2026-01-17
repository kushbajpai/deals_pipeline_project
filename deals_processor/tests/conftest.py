"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from deals_processor.main import create_app


@pytest.fixture
def app():
    """Fixture: Create FastAPI app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Fixture: Create TestClient for API testing.

    Args:
        app: FastAPI application instance.

    Yields:
        TestClient: FastAPI test client.
    """
    return TestClient(app)


@pytest.fixture
def base_url():
    """Fixture: Provide base URL for API endpoints.

    Yields:
        str: Base URL path.
    """
    return "/api/v1"
