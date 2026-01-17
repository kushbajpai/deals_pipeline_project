"""Deal service for business logic.

Services encapsulate business logic and follow the Single Responsibility Principle.
This service handles all deal-related operations.
"""

import logging
from typing import Optional
from uuid import uuid4

from deals_processor.core.exceptions import DuplicateError, NotFoundError, ValidationError
from deals_processor.models import Deal, DealStatus

logger = logging.getLogger(__name__)


class DealService:
    """Service for managing deals.

    Encapsulates all business logic related to deal operations.
    Uses dependency injection for flexibility and testability.
    """

    def __init__(self) -> None:
        """Initialize deal service."""
        # In-memory storage for demonstration
        # In production, this would be injected database/repository
        self._deals: dict[str, Deal] = {}
        logger.info("DealService initialized")

    def create_deal(
        self, title: str, description: Optional[str], amount: float
    ) -> Deal:
        """Create a new deal.

        Args:
            title: Deal title.
            description: Optional deal description.
            amount: Deal amount.

        Returns:
            Deal: Created deal instance.

        Raises:
            ValidationError: If validation fails.
        """
        if not title or not title.strip():
            raise ValidationError("Deal title cannot be empty")

        if amount <= 0:
            raise ValidationError("Deal amount must be positive")

        deal = Deal(
            id=str(uuid4()),
            title=title.strip(),
            description=description,
            amount=amount,
        )

        self._deals[deal.id] = deal
        logger.info(f"Created deal with id: {deal.id}")
        return deal

    def get_deal(self, deal_id: str) -> Deal:
        """Get a deal by ID.

        Args:
            deal_id: Deal identifier.

        Returns:
            Deal: The requested deal.

        Raises:
            NotFoundError: If deal not found.
        """
        deal = self._deals.get(deal_id)
        if deal is None:
            logger.warning(f"Deal not found: {deal_id}")
            raise NotFoundError("Deal", deal_id)
        return deal

    def list_deals(self, status: Optional[DealStatus] = None) -> list[Deal]:
        """List all deals, optionally filtered by status.

        Args:
            status: Optional status filter.

        Returns:
            list[Deal]: List of deals matching criteria.
        """
        deals = list(self._deals.values())
        if status:
            deals = [d for d in deals if d.status == status]
        logger.info(f"Retrieved {len(deals)} deals")
        return deals

    def update_deal(
        self,
        deal_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        status: Optional[DealStatus] = None,
    ) -> Deal:
        """Update an existing deal.

        Args:
            deal_id: Deal identifier.
            title: Optional new title.
            description: Optional new description.
            amount: Optional new amount.
            status: Optional new status.

        Returns:
            Deal: Updated deal instance.

        Raises:
            NotFoundError: If deal not found.
            ValidationError: If validation fails.
        """
        deal = self.get_deal(deal_id)

        if title is not None:
            if not title.strip():
                raise ValidationError("Deal title cannot be empty")
            deal.title = title.strip()

        if description is not None:
            deal.description = description

        if amount is not None:
            deal.update_amount(amount)

        if status is not None:
            deal.update_status(status)

        logger.info(f"Updated deal with id: {deal_id}")
        return deal

    def delete_deal(self, deal_id: str) -> None:
        """Delete a deal.

        Args:
            deal_id: Deal identifier.

        Raises:
            NotFoundError: If deal not found.
        """
        if deal_id not in self._deals:
            logger.warning(f"Attempted to delete non-existent deal: {deal_id}")
            raise NotFoundError("Deal", deal_id)

        del self._deals[deal_id]
        logger.info(f"Deleted deal with id: {deal_id}")

    def get_active_deals_count(self) -> int:
        """Get count of active deals.

        Returns:
            int: Number of active deals.
        """
        count = sum(1 for deal in self._deals.values() if deal.is_active())
        return count
