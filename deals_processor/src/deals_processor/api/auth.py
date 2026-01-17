"""Authentication route handlers for FastAPI application.

Provides endpoints for user registration, login, token refresh, and profile retrieval.
All endpoints follow REST conventions and use proper HTTP status codes.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from deals_processor.core.database import get_db_session
from deals_processor.core.exceptions import ValidationError, DuplicateError, UnauthorizedError
from deals_processor.core.security import get_current_user
from deals_processor.models.user import UserModel
from deals_processor.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    AccessTokenResponse,
    UserResponse,
    ChangePasswordRequest,
    RefreshTokenRequest,
)
from deals_processor.services.auth_service import AuthService, UserService

logger = logging.getLogger(__name__)


class AuthRouteHandler:
    """Handles all authentication-related HTTP endpoints.

    Provides user registration, login, token management, and profile endpoints.
    Uses dependency injection for database sessions and current user context.
    """

    def __init__(self):
        """Initialize authentication route handler."""
        self.router = APIRouter(prefix="/auth", tags=["authentication"])
        self._setup_routes()
        logger.info("AuthRouteHandler initialized")

    def _setup_routes(self) -> None:
        """Register all authentication routes with the router."""
        self.router.post("/register", response_model=TokenResponse)(self.register)
        self.router.post("/login", response_model=TokenResponse)(self.login)
        self.router.post("/refresh", response_model=AccessTokenResponse)(self.refresh_token)
        self.router.get("/me", response_model=UserResponse)(self.get_current_user_profile)
        self.router.post("/change-password")(self.change_password)
        logger.debug("Authentication routes registered")

    async def register(
        self,
        user_data: UserRegister,
        db: Session = Depends(get_db_session),
    ) -> TokenResponse:
        """Register a new user and return authentication tokens.

        Validates user input, checks for duplicate email, creates user account,
        and generates JWT tokens for immediate authentication.

        Args:
            user_data: User registration data (email, password, full_name).
            db: Database session.

        Returns:
            TokenResponse: Access token, refresh token, token type, and user info.

        Raises:
            HTTPException: If email already exists (409) or validation fails (400).
        """
        try:
            logger.info(f"Registration attempt for email: {user_data.email}")

            auth_service = AuthService(db)

            # Register user and get tokens
            tokens = auth_service.register_user(
                email=user_data.email,
                password=user_data.password,
                full_name=user_data.full_name,
            )

            logger.info(f"User registered successfully: {user_data.email}")
            return TokenResponse(**tokens)

        except DuplicateError as e:
            logger.warning(f"Registration failed - duplicate email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=e.message,
            )
        except ValidationError as e:
            logger.warning(f"Registration failed - validation error: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed",
            )

    async def login(
        self,
        credentials: UserLogin,
        db: Session = Depends(get_db_session),
    ) -> TokenResponse:
        """Authenticate user and return authentication tokens.

        Validates email/password combination, updates last login timestamp,
        and generates JWT tokens for API access.

        Args:
            credentials: Login credentials (email, password).
            db: Database session.

        Returns:
            TokenResponse: Access token, refresh token, token type, and user info.

        Raises:
            HTTPException: If credentials invalid (401) or user inactive (403).
        """
        try:
            logger.info(f"Login attempt for email: {credentials.email}")

            auth_service = AuthService(db)

            # Authenticate user and get tokens
            tokens = auth_service.login(
                email=credentials.email,
                password=credentials.password,
            )

            logger.info(f"User logged in successfully: {credentials.email}")
            return TokenResponse(**tokens)

        except UnauthorizedError as e:
            logger.warning(f"Login failed - invalid credentials: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
            )
        except ValidationError as e:
            logger.warning(f"Login failed - validation error: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed",
            )

    async def refresh_token(
        self,
        token_request: RefreshTokenRequest,
        db: Session = Depends(get_db_session),
    ) -> AccessTokenResponse:
        """Generate new access token using refresh token.

        Validates refresh token, verifies user is still active,
        and issues a new short-lived access token.

        Args:
            token_request: Refresh token request (refresh_token).
            db: Database session.

        Returns:
            AccessTokenResponse: New access token and token type.

        Raises:
            HTTPException: If refresh token invalid/expired (401).
        """
        try:
            logger.debug("Token refresh attempt")

            auth_service = AuthService(db)

            # Refresh access token
            new_tokens = auth_service.refresh_access_token(
                refresh_token=token_request.refresh_token,
            )

            logger.info("Access token refreshed successfully")
            return AccessTokenResponse(**new_tokens)

        except UnauthorizedError as e:
            logger.warning(f"Token refresh failed: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
            )
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed",
            )

    async def get_current_user_profile(
        self,
        current_user: UserModel = Depends(get_current_user),
    ) -> UserResponse:
        """Get current authenticated user's profile information.

        Returns user details including email, username, full name, role,
        and account status. Requires valid authentication token.

        Args:
            current_user: Current authenticated user from JWT token.

        Returns:
            UserResponse: User profile information.

        Raises:
            HTTPException: If user not authenticated (401).
        """
        try:
            logger.info(f"User profile requested: {current_user.id}")
            return UserResponse.from_orm(current_user)
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user profile",
            )

    async def change_password(
        self,
        password_request: ChangePasswordRequest,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> dict:
        """Change password for current authenticated user.

        Verifies old password is correct before updating to new password.
        Updates user record in database.

        Args:
            password_request: Password change request (old_password, new_password).
            current_user: Current authenticated user from JWT token.
            db: Database session.

        Returns:
            dict: Success message.

        Raises:
            HTTPException: If old password incorrect (401) or validation fails (400).
        """
        try:
            logger.info(f"Password change requested by user: {current_user.id}")

            user_service = UserService(db)

            # Change password
            user_service.change_password(
                user_id=current_user.id,
                old_password=password_request.old_password,
                new_password=password_request.new_password,
            )

            logger.info(f"Password changed successfully for user: {current_user.id}")
            return {"message": "Password changed successfully"}

        except UnauthorizedError as e:
            logger.warning(
                f"Password change failed for user {current_user.id}: "
                f"invalid old password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
            )
        except ValidationError as e:
            logger.warning(
                f"Password change failed for user {current_user.id}: {e.message}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            logger.error(f"Password change error for user {current_user.id}: {e}")


# Create route handler instance
auth_handler = AuthRouteHandler()

