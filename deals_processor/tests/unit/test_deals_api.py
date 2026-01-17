"""Unit tests for deal API endpoints."""

import pytest


@pytest.mark.unit
def test_list_deals_empty(client, base_url):
    """Test listing deals when empty.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    response = client.get(f"{base_url}/deals")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.unit
def test_create_deal(client, base_url):
    """Test creating a deal via API.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    deal_data = {
        "title": "Test Deal",
        "description": "Test Description",
        "amount": 1000.0,
        "status": "pending",
    }

    response = client.post(f"{base_url}/deals", json=deal_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Deal"
    assert data["amount"] == 1000.0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.unit
def test_create_deal_validation_error(client, base_url):
    """Test creating deal with invalid data.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    deal_data = {
        "title": "",
        "description": "Test",
        "amount": 1000.0,
    }

    response = client.post(f"{base_url}/deals", json=deal_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_get_deal(client, base_url):
    """Test getting a specific deal.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    # Create a deal
    deal_data = {
        "title": "Test Deal",
        "description": "Test",
        "amount": 500.0,
    }
    create_response = client.post(f"{base_url}/deals", json=deal_data)
    deal_id = create_response.json()["id"]

    # Get the deal
    response = client.get(f"{base_url}/deals/{deal_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == deal_id
    assert data["title"] == "Test Deal"


@pytest.mark.unit
def test_get_deal_not_found(client, base_url):
    """Test getting non-existent deal.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    response = client.get(f"{base_url}/deals/non-existent-id")

    assert response.status_code == 404


@pytest.mark.unit
def test_update_deal(client, base_url):
    """Test updating a deal.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    # Create a deal
    deal_data = {
        "title": "Original Title",
        "description": "Original",
        "amount": 100.0,
    }
    create_response = client.post(f"{base_url}/deals", json=deal_data)
    deal_id = create_response.json()["id"]

    # Update the deal
    update_data = {
        "title": "Updated Title",
        "amount": 200.0,
    }
    response = client.put(f"{base_url}/deals/{deal_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["amount"] == 200.0


@pytest.mark.unit
def test_delete_deal(client, base_url):
    """Test deleting a deal.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    # Create a deal
    deal_data = {
        "title": "Test Deal",
        "description": "Test",
        "amount": 100.0,
    }
    create_response = client.post(f"{base_url}/deals", json=deal_data)
    deal_id = create_response.json()["id"]

    # Delete the deal
    response = client.delete(f"{base_url}/deals/{deal_id}")

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"{base_url}/deals/{deal_id}")
    assert get_response.status_code == 404


@pytest.mark.unit
def test_active_deals_count(client, base_url):
    """Test getting active deals count.

    Args:
        client: FastAPI test client.
        base_url: Base API URL.
    """
    # Create and activate deals
    for i in range(3):
        deal_data = {
            "title": f"Deal {i}",
            "description": "Test",
            "amount": 100.0 * (i + 1),
            "status": "active" if i < 2 else "pending",
        }
        client.post(f"{base_url}/deals", json=deal_data)

    response = client.get(f"{base_url}/deals/stats/active-count")

    assert response.status_code == 200
    data = response.json()
    assert data["active_count"] == 2
