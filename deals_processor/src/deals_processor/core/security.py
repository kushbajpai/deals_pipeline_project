"""Security utilities for authentication and authorization.

Provides decorators and dependencies for FastAPI route protection,
role-based access control, and permission checking.
"""

import logging
from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from deals_processor.core.database import get_db_session
from deals_processor.core.exceptions import ForbiddenError, UnauthorizedError
from deals_processor.models.user import UserModel
from deals_processor.repositories.user_repository import UserRepository
from deals_processor.services.auth_service import AuthService

logger = logging.getLogger(__name__)


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value.

    Returns:
        Optional[str]: JWT token if valid header format, None otherwise.
    """
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db_session),
) -> UserModel:
    """Dependency to get current authenticated user from JWT token.

    Extracts JWT from Authorization header, validates it, and returns user.

    Args:
        request: FastAPI request object.
        db: Database session.

    Returns:
        UserModel: Authenticated user.

    Raises:
        HTTPException: If token missing, invalid, or expired (401).
        HTTPException: If user not found or inactive (401).
    """
    authorization = request.headers.get("Authorization")
    token = extract_token_from_header(authorization)

    if not token:
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auth_service = AuthService(db)
        token_data = auth_service.validate_token(token)
        user = token_data.get("user")

        if not user:
            logger.warning("User not found for valid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
    except UnauthorizedError as e:
        logger.warning(f"Token validation failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Dependency to get current user and verify admin role.

    Args:
        current_user: Current authenticated user.

    Returns:
        UserModel: Authenticated user with admin role.

    Raises:
        HTTPException: If user is not admin (403).
    """
    if current_user.role != "admin":
        logger.warning(f"Admin access denied for user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def get_current_analyst(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Dependency to get current user and verify analyst role.

    Args:
        current_user: Current authenticated user.

    Returns:
        UserModel: Authenticated user with analyst role.

    Raises:
        HTTPException: If user is not analyst (403).
    """
    if current_user.role not in ["admin", "analyst"]:
        logger.warning(f"Analyst access denied for user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required",
        )
    return current_user


async def get_current_partner(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Dependency to get current user and verify partner role.

    Args:
        current_user: Current authenticated user.

    Returns:
        UserModel: Authenticated user with partner role.

    Raises:
        HTTPException: If user is not partner (403).
    """
    if current_user.role not in ["admin", "partner"]:
        logger.warning(f"Partner access denied for user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Partner access required",
        )
    return current_user


def require_role(*roles: str) -> Callable:
    """Decorator to require specific roles for endpoint access.

    Usage:
        @require_role("admin", "analyst")
        async def some_endpoint(current_user: UserModel = Depends(get_current_user)):
            ...

    Args:
        *roles: Required role names.

    Returns:
        Callable: Decorated endpoint function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> any:
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                logger.error("current_user not found in kwargs")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if current_user.role not in roles:
                logger.warning(
                    f"Access denied for user {current_user.id}: "
                    f"requires {roles}, has {current_user.role}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"One of {roles} required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_permission(permission: str) -> Callable:
    """Decorator to require specific permission for endpoint access.

    Usage:
        @require_permission("create_deal")
        async def create_endpoint(current_user: UserModel = Depends(get_current_user)):
            ...

    Args:
        permission: Required permission name.

    Returns:
        Callable: Decorated endpoint function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> any:
            current_user = kwargs.get("current_user")
            if not current_user:
                logger.error("current_user not found in kwargs")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Define role permissions mapping
            role_permissions = {
                "admin": ["*"],  # Admin has all permissions
                "analyst": [
                    "create_deal",
                    "edit_deal",
                    "view_reports",
                    "create_memo",
                ],
                "partner": ["comment", "vote", "approve_deal", "decline_deal"],
            }

            allowed_permissions = role_permissions.get(current_user.role, [])

            if "*" not in allowed_permissions and permission not in allowed_permissions:
                logger.warning(
                    f"Permission denied for user {current_user.id}: "
                    f"requires {permission}, has {allowed_permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def admin_only(func: Callable) -> Callable:
    """Decorator to restrict endpoint to admin users only.

    Usage:
        @admin_only
        async def admin_endpoint(current_user: UserModel = Depends(get_current_user)):
            ...

    Args:
        func: Endpoint function to decorate.

    Returns:
        Callable: Decorated endpoint function.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> any:
        current_user = kwargs.get("current_user")
        if not current_user or current_user.role != "admin":
            logger.warning(
                f"Admin-only access denied for user: "
                f"{current_user.id if current_user else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        return await func(*args, **kwargs)

    return wrapper


def analyst_only(func: Callable) -> Callable:
    """Decorator to restrict endpoint to analyst+ users.

    Usage:
        @analyst_only
        async def analyst_endpoint(current_user: UserModel = Depends(get_current_user)):
            ...

    Args:
        func: Endpoint function to decorate.

    Returns:
        Callable: Decorated endpoint function.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> any:
        current_user = kwargs.get("current_user")
        if not current_user or current_user.role not in ["admin", "analyst"]:
            logger.warning(
                f"Analyst access denied for user: "
                f"{current_user.id if current_user else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Analyst access required",
            )
        return await func(*args, **kwargs)

    return wrapper


def partner_only(func: Callable) -> Callable:
    """Decorator to restrict endpoint to partner+ users.

    Usage:
        @partner_only
        async def partner_endpoint(current_user: UserModel = Depends(get_current_user)):
            ...

    Args:
        func: Endpoint function to decorate.

    Returns:
        Callable: Decorated endpoint function.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> any:
        current_user = kwargs.get("current_user")
        if not current_user or current_user.role not in ["admin", "partner"]:
            logger.warning(
                f"Partner access denied for user: "
                f"{current_user.id if current_user else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Partner access required",
            )
        return await func(*args, **kwargs)

    return wrapper


def log_authorization_attempt(user_id: int, action: str, allowed: bool) -> None:
    """Log authorization attempt for audit trail.

    Args:
        user_id: User ID attempting action.
        action: Action attempted.
        allowed: Whether action was allowed.
    """
    if allowed:
        logger.info(f"Authorization ALLOWED: User {user_id} - {action}")
    else:
        logger.warning(f"Authorization DENIED: User {user_id} - {action}")
