"""Unit tests for deal service."""

import pytest

from deals_processor.core.exceptions import NotFoundError, ValidationError
from deals_processor.models import DealStatus
from deals_processor.services import DealService


@pytest.fixture
def service():
    """Fixture: Create DealService instance.

    Yields:
        DealService: Service instance.
    """
    return DealService()


@pytest.mark.unit
def test_create_deal(service):
    """Test creating a deal.

    Args:
        service: DealService instance.
    """
    deal = service.create_deal(
        title="Test Deal", description="Test Description", amount=1000.0
    )

    assert deal.id is not None
    assert deal.title == "Test Deal"
    assert deal.description == "Test Description"
    assert deal.amount == 1000.0
    assert deal.status == DealStatus.PENDING


@pytest.mark.unit
def test_create_deal_validation_empty_title(service):
    """Test creating deal with empty title raises error.

    Args:
        service: DealService instance.
    """
    with pytest.raises(ValidationError):
        service.create_deal(title="", description="Test", amount=100.0)


@pytest.mark.unit
def test_create_deal_validation_negative_amount(service):
    """Test creating deal with negative amount raises error.

    Args:
        service: DealService instance.
    """
    with pytest.raises(ValidationError):
        service.create_deal(title="Test", description="Test", amount=-100.0)


@pytest.mark.unit
def test_get_deal(service):
    """Test retrieving a deal.

    Args:
        service: DealService instance.
    """
    created_deal = service.create_deal(
        title="Test Deal", description="Test Description", amount=1000.0
    )

    retrieved_deal = service.get_deal(created_deal.id)

    assert retrieved_deal.id == created_deal.id
    assert retrieved_deal.title == created_deal.title


@pytest.mark.unit
def test_get_deal_not_found(service):
    """Test getting non-existent deal raises error.

    Args:
        service: DealService instance.
    """
    with pytest.raises(NotFoundError):
        service.get_deal("non-existent-id")


@pytest.mark.unit
def test_list_deals(service):
    """Test listing deals.

    Args:
        service: DealService instance.
    """
    service.create_deal(title="Deal 1", description=None, amount=500.0)
    service.create_deal(title="Deal 2", description=None, amount=1000.0)

    deals = service.list_deals()

    assert len(deals) == 2


@pytest.mark.unit
def test_list_deals_by_status(service):
    """Test listing deals filtered by status.

    Args:
        service: DealService instance.
    """
    deal1 = service.create_deal(title="Deal 1", description=None, amount=500.0)
    deal2 = service.create_deal(title="Deal 2", description=None, amount=1000.0)

    service.update_deal(deal1.id, status=DealStatus.ACTIVE)

    active_deals = service.list_deals(status=DealStatus.ACTIVE)

    assert len(active_deals) == 1
    assert active_deals[0].id == deal1.id


@pytest.mark.unit
def test_update_deal(service):
    """Test updating a deal.

    Args:
        service: DealService instance.
    """
    deal = service.create_deal(title="Original", description=None, amount=100.0)

    updated = service.update_deal(deal.id, title="Updated", amount=200.0)

    assert updated.title == "Updated"
    assert updated.amount == 200.0


@pytest.mark.unit
def test_delete_deal(service):
    """Test deleting a deal.

    Args:
        service: DealService instance.
    """
    deal = service.create_deal(title="Test", description=None, amount=100.0)

    service.delete_deal(deal.id)

    with pytest.raises(NotFoundError):
        service.get_deal(deal.id)


@pytest.mark.unit
def test_get_active_deals_count(service):
    """Test getting active deals count.

    Args:
        service: DealService instance.
    """
    deal1 = service.create_deal(title="Deal 1", description=None, amount=100.0)
    deal2 = service.create_deal(title="Deal 2", description=None, amount=200.0)

    service.update_deal(deal1.id, status=DealStatus.ACTIVE)

    count = service.get_active_deals_count()

    assert count == 1
