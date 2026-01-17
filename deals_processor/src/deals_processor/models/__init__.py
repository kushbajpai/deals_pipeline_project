"""Domain models for the application.

These models represent the core business entities and follow the Domain Model pattern.
They are decoupled from persistence and API concerns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class DealStatus(str, Enum):
    """Deal status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"


@dataclass
class Deal:
    """Domain model for a Deal.

    Represents a deal entity with all business-relevant attributes.
    Uses dataclass for simplicity and immutability where appropriate.

    Attributes:
        id: Unique deal identifier.
        title: Deal title or name.
        description: Optional deal description.
        amount: Deal monetary amount.
        status: Current deal status.
        created_at: Timestamp when deal was created.
        updated_at: Timestamp when deal was last updated.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: Optional[str] = None
    amount: float = 0.0
    status: DealStatus = DealStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_status(self, new_status: DealStatus) -> None:
        """Update deal status and timestamp.

        Args:
            new_status: New status for the deal.
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def update_amount(self, new_amount: float) -> None:
        """Update deal amount and timestamp.

        Args:
            new_amount: New amount for the deal.

        Raises:
            ValueError: If amount is not positive.
        """
        if new_amount <= 0:
            raise ValueError("Amount must be positive")
        self.amount = new_amount
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Check if deal is currently active.

        Returns:
            True if deal status is ACTIVE, False otherwise.
        """
        return self.status == DealStatus.ACTIVE
