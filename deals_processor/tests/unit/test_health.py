"""Unit tests for health check endpoints."""

import pytest


@pytest.mark.unit
def test_health_check(client, base_url):
    """Test health check endpoint.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    response = client.get(f"{base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.unit
def test_health_check_contains_version(client, base_url):
    """Test health check includes version.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    response = client.get(f"{base_url}/health")
    data = response.json()
    assert "version" in data
    assert isinstance(data["version"], str)
