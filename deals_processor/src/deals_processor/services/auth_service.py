"""Authentication service for user registration and login.

Handles user registration, login, and token management following
security best practices with password hashing and JWT tokens.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from deals_processor.core.auth import PasswordHasher, JWTTokenManager
from deals_processor.core.config import get_settings
from deals_processor.core.exceptions import (
    ValidationError,
    DuplicateError,
    UnauthorizedError,
)
from deals_processor.models.user import UserModel, RoleModel
from deals_processor.repositories.user_repository import UserRepository, RoleRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations.

    Handles user registration, login, token generation, and validation.
    Implements security best practices for password handling and JWT tokens.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize auth service.

        Args:
            db_session: SQLAlchemy database session.
        """
        settings = get_settings()
        self.user_repo = UserRepository(db_session)
        self.role_repo = RoleRepository(db_session)
        self.password_hasher = PasswordHasher(rounds=settings.bcrypt_rounds)
        self.token_manager = JWTTokenManager(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
            refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
        )
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_session = db_session

    def register_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "user",
    ) -> dict:
        """Register a new user.

        Args:
            email: User email address.
            password: User password (plaintext).
            full_name: User's full name (optional).
            role: User role (default: user).

        Returns:
            dict: Contains access_token, refresh_token, token_type, and user info.

        Raises:
            ValidationError: If email/password invalid.
            DuplicateError: If email already exists.
        """
        # Validate inputs
        email = email.lower().strip()
        if not email or "@" not in email:
            raise ValidationError("Invalid email format")

        if not password or len(password) < self.settings.password_min_length:
            raise ValidationError(
                f"Password must be at least {self.settings.password_min_length} characters"
            )

        # Check if email exists
        if self.user_repo.email_exists(email):
            self.logger.warning(f"Registration attempt with existing email: {email}")
            raise DuplicateError("User", email)

        # Hash password
        password_hash = self.password_hasher.hash_password(password)

        # Create user
        try:
            user = self.user_repo.create(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role=role,
                is_active=True,
            )
            self.logger.info(f"User registered successfully: {email}")

            # Generate tokens for immediate authentication
            access_token = self.token_manager.create_access_token(
                user_id=user.id,
                email=user.email,
                role=user.role,
            )
            refresh_token = self.token_manager.create_refresh_token(user_id=user.id)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": user.to_dict(),
            }
        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
            raise ValidationError("Failed to register user")

    def login(self, email: str, password: str) -> dict:
        """Authenticate user and generate tokens.

        Args:
            email: User email.
            password: User password (plaintext).

        Returns:
            dict: Contains access_token, refresh_token, and user info.

        Raises:
            UnauthorizedError: If credentials invalid.
        """
        email = email.lower().strip()

        # Find user
        user = self.user_repo.find_by_email(email)
        if not user:
            self.logger.warning(f"Login attempt with non-existent email: {email}")
            raise UnauthorizedError("Invalid email or password")

        # Check if active
        if not user.is_active:
            self.logger.warning(f"Login attempt with inactive user: {email}")
            raise UnauthorizedError("Account is inactive")

        # Verify password
        if not self.password_hasher.verify_password(password, user.password_hash):
            self.logger.warning(f"Failed login attempt for user: {email}")
            raise UnauthorizedError("Invalid email or password")

        # Update last login
        user.update_last_login()
        self.db_session.commit()

        # Generate tokens
        access_token = self.token_manager.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        refresh_token = self.token_manager.create_refresh_token(user_id=user.id)

        self.logger.info(f"User logged in successfully: {email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            dict: New access token.

        Raises:
            UnauthorizedError: If refresh token invalid.
        """
        try:
            payload = self.token_manager.decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid token type")

            user_id = int(payload.get("sub"))
            user = self.user_repo.read(user_id)

            if not user or not user.is_active:
                raise UnauthorizedError("User not found or inactive")

            access_token = self.token_manager.create_access_token(
                user_id=user.id,
                email=user.email,
                role=user.role,
            )

            self.logger.info(f"Access token refreshed for user: {user.id}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
            }
        except UnauthorizedError:
            raise
        except Exception as e:
            self.logger.error(f"Error refreshing token: {e}")
            raise UnauthorizedError("Invalid refresh token")

    def validate_token(self, token: str) -> dict:
        """Validate and decode authentication token.

        Args:
            token: JWT token to validate.

        Returns:
            dict: Decoded token payload with user info.

        Raises:
            UnauthorizedError: If token invalid or expired.
        """
        try:
            payload = self.token_manager.decode_token(token)

            if payload.get("type") != "access":
                raise UnauthorizedError("Invalid token type")

            user_id = int(payload.get("sub"))
            user = self.user_repo.read(user_id)

            if not user or not user.is_active:
                raise UnauthorizedError("User not found or inactive")

            return {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "user": user,
            }
        except UnauthorizedError:
            raise
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            raise UnauthorizedError("Invalid token")


class UserService:
    """Service for user management operations.

    Handles user CRUD operations, role management, and user administration.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize user service.

        Args:
            db_session: SQLAlchemy database session.
        """
        self.user_repo = UserRepository(db_session)
        self.role_repo = RoleRepository(db_session)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_session = db_session

    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user by ID.

        Args:
            user_id: User ID.

        Returns:
            Optional[dict]: User data or None if not found.
        """
        user = self.user_repo.read(user_id)
        if user:
            self.logger.debug(f"Retrieved user: {user_id}")
            return user.to_dict()
        return None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email.

        Args:
            email: User email.

        Returns:
            Optional[dict]: User data or None if not found.
        """
        user = self.user_repo.find_by_email(email)
        if user:
            self.logger.debug(f"Retrieved user by email: {email}")
            return user.to_dict()
        return None

    def list_users(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """List all active users with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[dict]: List of user data.
        """
        users = self.user_repo.find_active_users(skip=skip, limit=limit)
        self.logger.debug(f"Listed {len(users)} users")
        return [user.to_dict() for user in users]

    def list_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """List users by role.

        Args:
            role: Role name to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[dict]: List of user data.
        """
        users = self.user_repo.find_by_role(role, skip=skip, limit=limit)
        self.logger.debug(f"Listed {len(users)} users with role {role}")
        return [user.to_dict() for user in users]

    def update_user(self, user_id: int, **kwargs) -> Optional[dict]:
        """Update user (admin only).

        Args:
            user_id: User ID to update.
            **kwargs: Fields to update (full_name, role, is_active, etc).

        Returns:
            Optional[dict]: Updated user data or None if not found.
        """
        # Prevent password updates through this method
        if "password_hash" in kwargs or "password" in kwargs:
            raise ValidationError("Use change_password for password updates")

        user = self.user_repo.update(user_id, **kwargs)
        if user:
            self.logger.info(f"Updated user: {user_id}")
            return user.to_dict()
        return None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password.

        Args:
            user_id: User ID.
            old_password: Current password (plaintext).
            new_password: New password (plaintext).

        Returns:
            bool: True if successful.

        Raises:
            ValidationError: If old password incorrect or new password invalid.
            ValueError: If user not found.
        """
        settings = get_settings()
        user = self.user_repo.read(user_id)

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Verify old password
        hasher = PasswordHasher(rounds=settings.bcrypt_rounds)
        if not hasher.verify_password(old_password, user.password_hash):
            raise ValidationError("Current password is incorrect")

        # Validate new password
        if not new_password or len(new_password) < settings.password_min_length:
            raise ValidationError(
                f"New password must be at least {settings.password_min_length} characters"
            )

        # Hash and update
        new_hash = hasher.hash_password(new_password)
        self.user_repo.update(user_id, password_hash=new_hash)

        self.logger.info(f"Password changed for user: {user_id}")
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account (soft delete).

        Args:
            user_id: User ID to deactivate.

        Returns:
            bool: True if successful.
        """
        user = self.user_repo.update(user_id, is_active=False)
        if user:
            self.logger.info(f"User deactivated: {user_id}")
            return True
        return False

    def activate_user(self, user_id: int) -> bool:
        """Activate user account.

        Args:
            user_id: User ID to activate.

        Returns:
            bool: True if successful.
        """
        user = self.user_repo.update(user_id, is_active=True)
        if user:
            self.logger.info(f"User activated: {user_id}")
            return True
        return False

    def get_role(self, role_id: int) -> Optional[dict]:
        """Get role by ID.

        Args:
            role_id: Role ID.

        Returns:
            Optional[dict]: Role data or None if not found.
        """
        role = self.role_repo.read(role_id)
        if role:
            return role.to_dict()
        return None

    def list_roles(self) -> list[dict]:
        """List all active roles.

        Returns:
            list[dict]: List of role data.
        """
        roles = self.role_repo.find_all_active()
        return [role.to_dict() for role in roles]

    def get_user_count_by_role(self, role: str) -> int:
        """Get count of users with specific role.

        Args:
            role: Role name.

        Returns:
            int: Count of users.
        """
        return self.user_repo.count_by_role(role)
