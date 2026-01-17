"""User and Role domain models for authentication and authorization.

Implements ORM models for user accounts and roles following the established
BaseModel pattern with proper relationships and timestamps.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from deals_processor.core.database import Base


class RoleModel(Base):
    """Role ORM model for role-based access control.

    Represents roles (admin, analyst, partner) with descriptions and
    hierarchy levels for flexible permission management.
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[Optional[int]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
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
        """String representation of Role."""
        return f"<RoleModel(id={self.id}, name={self.name})>"

    def to_dict(self) -> dict:
        """Convert role model to dictionary.

        Returns:
            dict: Role data as dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class UserModel(Base):
    """User ORM model for authentication and authorization.

    Represents user accounts with credentials, role associations,
    and profile information.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="user", index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
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

    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self) -> dict:
        """Convert user model to dictionary (excludes password hash).

        Returns:
            dict: User data as dictionary.
        """
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def update_last_login(self) -> None:
        """Update last login timestamp to current time."""
        self.last_login = datetime.utcnow()
