"""SQLAlchemy ORM models for database persistence.

All models follow OOP principles and inherit from BaseModel
which provides common functionality like timestamps.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from deals_processor.core.database import Base


class BaseModel(Base):
    """Abstract base model providing common columns for all entities.
    
    Implements the Mixin pattern to share timestamp and ID functionality.
    All database models should inherit from this class.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


class DealModel(BaseModel):
    """Deal ORM model for Kanban pipeline management.
    
    Represents a deal entity with pipeline stage tracking and investment details.
    Stages: Sourced → Screen → Diligence → IC → Invested → Passed
    """

    __tablename__ = "deals"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, default="Sourced", index=True)
    round: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    check_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)

    def __repr__(self) -> str:
        """String representation of Deal."""
        return f"<DealModel(id={self.id}, name={self.name}, stage={self.stage})>"

    def to_dict(self) -> dict:
        """Convert model instance to dictionary.
        
        Returns:
            dict: Model data as dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "company_url": self.company_url,
            "owner": self.owner,
            "stage": self.stage,
            "round": self.round,
            "check_size": self.check_size,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ActivityModel(BaseModel):
    """Activity log model for deal pipeline auditing.
    
    Records all activities related to deals, especially stage changes.
    Provides complete audit trail for compliance and tracking.
    """

    __tablename__ = "activities"

    deal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """String representation of Activity."""
        return f"<ActivityModel(id={self.id}, deal_id={self.deal_id}, type={self.activity_type})>"

    def to_dict(self) -> dict:
        """Convert model instance to dictionary.
        
        Returns:
            dict: Model data as dictionary.
        """
        return {
            "id": self.id,
            "deal_id": self.deal_id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
