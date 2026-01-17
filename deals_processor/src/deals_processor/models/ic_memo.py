"""IC Memo models for deal evaluation and versioning."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from deals_processor.core.database import Base


class ICMemoModel(Base):
    """IC Memo ORM model for structured deal evaluation.
    
    Represents the current version of an IC memo with versioning support.
    Each save creates a new version entry.
    """

    __tablename__ = "ic_memos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deal_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    last_updated_by: Mapped[int] = mapped_column(Integer, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Memo sections (current version)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    market: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    product: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    traction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    open_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
        """String representation of IC Memo."""
        return f"<ICMemoModel(id={self.id}, deal_id={self.deal_id}, version={self.current_version})>"

    def to_dict(self) -> dict:
        """Convert model instance to dictionary.
        
        Returns:
            dict: Model data as dictionary.
        """
        return {
            "id": self.id,
            "deal_id": self.deal_id,
            "created_by": self.created_by,
            "last_updated_by": self.last_updated_by,
            "current_version": self.current_version,
            "summary": self.summary,
            "market": self.market,
            "product": self.product,
            "traction": self.traction,
            "risks": self.risks,
            "open_questions": self.open_questions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ICMemoVersionModel(Base):
    """IC Memo Version history ORM model.
    
    Stores complete snapshots of each IC memo version for audit trail and recovery.
    """

    __tablename__ = "ic_memo_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    memo_id: Mapped[int] = mapped_column(Integer, ForeignKey("ic_memos.id"), nullable=False, index=True)
    deal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Complete memo content snapshot
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    market: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    product: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    traction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    open_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Version metadata
    change_summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of IC Memo Version."""
        return f"<ICMemoVersionModel(memo_id={self.memo_id}, version={self.version_number})>"

    def to_dict(self) -> dict:
        """Convert model instance to dictionary.
        
        Returns:
            dict: Model data as dictionary.
        """
        return {
            "id": self.id,
            "memo_id": self.memo_id,
            "deal_id": self.deal_id,
            "version_number": self.version_number,
            "created_by": self.created_by,
            "summary": self.summary,
            "market": self.market,
            "product": self.product,
            "traction": self.traction,
            "risks": self.risks,
            "open_questions": self.open_questions,
            "change_summary": self.change_summary,
            "created_at": self.created_at,
        }
