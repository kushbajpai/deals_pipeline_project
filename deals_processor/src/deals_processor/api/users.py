"""User management API endpoints.

Provides endpoints for managing users and their roles.
Only accessible by Admin users.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from deals_processor.core.database import get_db_session
from deals_processor.core.security import get_current_user
from deals_processor.models.user import UserModel
from deals_processor.schemas.user import UserSchema, UserUpdateSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


class RoleUpdate(BaseModel):
    """Schema for role update requests."""

    role: str


def check_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Check that current user is admin.
    
    Args:
        current_user: Currently authenticated user.
        
    Returns:
        UserModel: The current user if admin.
        
    Raises:
        HTTPException: If user is not admin.
    """
    # Handle both string role and RoleModel object
    user_role = current_user.role
    if hasattr(user_role, 'name'):
        user_role = user_role.name.lower()
    elif isinstance(user_role, str):
        user_role = user_role.lower()
    
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access user management",
        )
    return current_user


@router.get("", response_model=List[UserSchema])
async def list_users(
    db: Session = Depends(get_db_session),
    admin: UserModel = Depends(check_admin),
) -> List[UserSchema]:
    """List all users.
    
    Args:
        db: Database session.
        admin: Verified admin user.
        
    Returns:
        List[UserSchema]: List of all users.
    """
    users = db.query(UserModel).all()
    logger.info(f"Admin {admin.email} retrieved user list ({len(users)} users)")
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    admin: UserModel = Depends(check_admin),
) -> UserSchema:
    """Get a specific user by ID.
    
    Args:
        user_id: ID of user to retrieve.
        db: Database session.
        admin: Verified admin user.
        
    Returns:
        UserSchema: User details.
        
    Raises:
        HTTPException: If user not found.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    logger.info(f"Admin {admin.email} retrieved user {user.email}")
    return user


@router.put("/{user_id}/role", response_model=UserSchema)
async def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db_session),
    admin: UserModel = Depends(check_admin),
) -> UserSchema:
    """Update a user's role.
    
    Args:
        user_id: ID of user to update.
        role_update: New role data.
        db: Database session.
        admin: Verified admin user.
        
    Returns:
        UserSchema: Updated user.
        
    Raises:
        HTTPException: If user not found or invalid role.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    new_role = role_update.role.lower()
    valid_roles = ["admin", "analyst", "partner", "user"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {new_role}. Must be one of {valid_roles}",
        )
    
    # Prevent removing last admin
    current_role = user.role if isinstance(user.role, str) else user.role.name.lower()
    if new_role != "admin" and current_role.lower() == "admin":
        admin_count = db.query(UserModel).filter(UserModel.role == "admin").count()
        if admin_count == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin user",
            )
    
    old_role = user.role
    user.role = new_role
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin {admin.email} changed {user.email} role from {old_role} to {new_role}")
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdateSchema,
    db: Session = Depends(get_db_session),
    admin: UserModel = Depends(check_admin),
) -> UserSchema:
    """Update user details (activate/deactivate).
    
    Args:
        user_id: ID of user to update.
        user_update: User update data.
        db: Database session.
        admin: Verified admin user.
        
    Returns:
        UserSchema: Updated user.
        
    Raises:
        HTTPException: If user not found.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user_update.is_active is not None:
        # Prevent deactivating last admin
        current_role = user.role if isinstance(user.role, str) else user.role.name.lower()
        if not user_update.is_active and current_role.lower() == "admin":
            admin_count = db.query(UserModel).filter(
                UserModel.is_active == True,
                UserModel.role.has(name="ADMIN")
            ).count()
            if admin_count == 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the last admin user",
                )
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin {admin.email} updated user {user.email}")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    admin: UserModel = Depends(check_admin),
) -> None:
    """Delete a user.
    
    Args:
        user_id: ID of user to delete.
        db: Database session.
        admin: Verified admin user.
        
    Raises:
        HTTPException: If user not found or last admin.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent deleting last admin
    current_role = user.role if isinstance(user.role, str) else user.role.name.lower()
    if current_role.lower() == "admin":
        admin_count = db.query(UserModel).filter(
            UserModel.role.has(name="ADMIN")
        ).count()
        if admin_count == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user",
            )
    
    db.delete(user)
    db.commit()
    
    logger.info(f"Admin {admin.email} deleted user {user.email}")
