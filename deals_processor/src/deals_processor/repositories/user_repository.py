"""Repository classes for User and Role data access.

Implements repository pattern for user and role management,
extending BaseRepository with specific queries.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from deals_processor.models.user import UserModel, RoleModel
from deals_processor.repositories.deal_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[UserModel]):
    """Repository for User model data access.

    Handles user-specific queries including finding by email,
    checking existence, and managing user lifecycle.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize user repository.

        Args:
            db_session: SQLAlchemy database session.
        """
        super().__init__(db_session, UserModel)
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_by_email(self, email: str) -> Optional[UserModel]:
        """Find user by email address.

        Args:
            email: User email to search for.

        Returns:
            Optional[UserModel]: User if found, None otherwise.
        """
        try:
            user = self.db.query(self.model).filter(
                self.model.email == email.lower()
            ).first()
            if user:
                self.logger.debug(f"Found user by email: {email}")
            return user
        except Exception as e:
            self.logger.error(f"Error finding user by email: {e}")
            return None

    def find_by_username(self, username: str) -> Optional[UserModel]:
        """Find user by username.

        Args:
            username: Username to search for.

        Returns:
            Optional[UserModel]: User if found, None otherwise.
        """
        try:
            user = self.db.query(self.model).filter(
                self.model.username == username
            ).first()
            if user:
                self.logger.debug(f"Found user by username: {username}")
            return user
        except Exception as e:
            self.logger.error(f"Error finding user by username: {e}")
            return None

    def email_exists(self, email: str) -> bool:
        """Check if email already exists in system.

        Args:
            email: Email to check.

        Returns:
            bool: True if email exists, False otherwise.
        """
        try:
            exists = self.db.query(self.model).filter(
                self.model.email == email.lower()
            ).first() is not None
            return exists
        except Exception as e:
            self.logger.error(f"Error checking email existence: {e}")
            return False

    def find_by_role(self, role: str, skip: int = 0, limit: int = 100) -> list[UserModel]:
        """Find all users with specific role.

        Args:
            role: Role name to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[UserModel]: Users with specified role.
        """
        try:
            users = self.db.query(self.model).filter(
                self.model.role == role,
                self.model.is_active == True
            ).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(users)} users with role {role}")
            return users
        except Exception as e:
            self.logger.error(f"Error finding users by role: {e}")
            return []

    def find_active_users(self, skip: int = 0, limit: int = 100) -> list[UserModel]:
        """Find all active users.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[UserModel]: Active users.
        """
        try:
            users = self.db.query(self.model).filter(
                self.model.is_active == True
            ).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(users)} active users")
            return users
        except Exception as e:
            self.logger.error(f"Error finding active users: {e}")
            return []

    def count_by_role(self, role: str) -> int:
        """Count users with specific role.

        Args:
            role: Role name to filter by.

        Returns:
            int: Count of users with that role.
        """
        try:
            count = self.db.query(self.model).filter(
                self.model.role == role
            ).count()
            return count
        except Exception as e:
            self.logger.error(f"Error counting users by role: {e}")
            return 0


class RoleRepository(BaseRepository[RoleModel]):
    """Repository for Role model data access.

    Handles role-specific queries including finding by name,
    checking existence, and role hierarchy management.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize role repository.

        Args:
            db_session: SQLAlchemy database session.
        """
        super().__init__(db_session, RoleModel)
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_by_name(self, name: str) -> Optional[RoleModel]:
        """Find role by name.

        Args:
            name: Role name to search for.

        Returns:
            Optional[RoleModel]: Role if found, None otherwise.
        """
        try:
            role = self.db.query(self.model).filter(
                self.model.name == name
            ).first()
            if role:
                self.logger.debug(f"Found role: {name}")
            return role
        except Exception as e:
            self.logger.error(f"Error finding role by name: {e}")
            return None

    def find_all_active(self) -> list[RoleModel]:
        """Find all active roles.

        Returns:
            list[RoleModel]: Active roles.
        """
        try:
            roles = self.db.query(self.model).filter(
                self.model.is_active == True
            ).all()
            self.logger.debug(f"Found {len(roles)} active roles")
            return roles
        except Exception as e:
            self.logger.error(f"Error finding active roles: {e}")
            return []

    def role_exists(self, name: str) -> bool:
        """Check if role exists.

        Args:
            name: Role name to check.

        Returns:
            bool: True if role exists, False otherwise.
        """
        try:
            exists = self.db.query(self.model).filter(
                self.model.name == name
            ).first() is not None
            return exists
        except Exception as e:
            self.logger.error(f"Error checking role existence: {e}")
            return False

    def get_default_roles(self) -> list[RoleModel]:
        """Get the three default roles: admin, analyst, partner.

        Returns:
            list[RoleModel]: Default roles in priority order.
        """
        default_role_names = ["admin", "analyst", "partner"]
        roles = []
        for name in default_role_names:
            role = self.find_by_name(name)
            if role:
                roles.append(role)
        return roles
