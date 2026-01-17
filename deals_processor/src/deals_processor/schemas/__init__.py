"""Pydantic schemas for request/response validation.

Schemas define the structure and validation rules for API request and response bodies.
They follow the Data Transfer Object (DTO) pattern.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DealStatus(str, Enum):
    """Deal status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class DealStage(str, Enum):
    """Deal pipeline stage enumeration."""

    SOURCED = "Sourced"
    SCREEN = "Screen"
    DILIGENCE = "Diligence"
    IC = "IC"
    INVESTED = "Invested"
    PASSED = "Passed"


class DealBase(BaseModel):
    """Base schema for deal data.

    Attributes:
        name: Deal name/title.
        company_url: Company website URL.
        owner: Deal owner/analyst.
        stage: Current pipeline stage.
        round: Investment round.
        check_size: Investment check size.
        status: Deal status.
    """

    name: str = Field(..., min_length=1, max_length=255, description="Deal name")
    company_url: Optional[str] = Field(None, max_length=500, description="Company URL")
    owner: str = Field(..., min_length=1, max_length=255, description="Deal owner")
    stage: DealStage = Field(default=DealStage.SOURCED, description="Pipeline stage")
    round: Optional[str] = Field(None, max_length=100, description="Investment round")
    check_size: Optional[float] = Field(None, gt=0, description="Check size amount")
    status: DealStatus = Field(default=DealStatus.ACTIVE, description="Deal status")


class DealCreate(DealBase):
    """Schema for creating a new deal."""

    pass


class DealUpdate(BaseModel):
    """Schema for updating an existing deal.

    All fields are optional to support partial updates.
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Deal name"
    )
    company_url: Optional[str] = Field(None, max_length=500, description="Company URL")
    owner: Optional[str] = Field(None, min_length=1, max_length=255, description="Deal owner")
    stage: Optional[DealStage] = Field(None, description="Pipeline stage")
    round: Optional[str] = Field(None, max_length=100, description="Investment round")
    check_size: Optional[float] = Field(None, gt=0, description="Check size amount")
    status: Optional[DealStatus] = Field(None, description="Deal status")


class DealStageUpdate(BaseModel):
    """Schema for updating deal stage (used for Kanban drag-and-drop).

    Attributes:
        stage: New pipeline stage.
    """

    stage: DealStage = Field(..., description="New pipeline stage")


class Deal(DealBase):
    """Schema for deal response.

    Attributes:
        id: Unique deal identifier.
        created_at: Timestamp when deal was created.
        updated_at: Timestamp when deal was last updated.
    """

    id: int = Field(..., description="Deal ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class ActivityCreate(BaseModel):
    """Schema for creating an activity record.

    Attributes:
        deal_id: Associated deal ID.
        user_id: User who performed the activity.
        activity_type: Type of activity (e.g., "stage_change").
        description: Activity description.
        old_value: Previous value (if applicable).
        new_value: New value (if applicable).
    """

    deal_id: int = Field(..., description="Deal ID")
    user_id: int = Field(..., description="User ID")
    activity_type: str = Field(..., max_length=100, description="Activity type")
    description: str = Field(..., description="Activity description")
    old_value: Optional[str] = Field(None, max_length=255, description="Old value")
    new_value: Optional[str] = Field(None, max_length=255, description="New value")


class Activity(ActivityCreate):
    """Schema for activity response.

    Attributes:
        id: Unique activity identifier.
        created_at: Timestamp when activity was created.
        updated_at: Timestamp when activity was last updated.
    """

    id: int = Field(..., description="Activity ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class HealthCheck(BaseModel):
    """Schema for health check response.

    Attributes:
        status: Application status.
        version: Application version.
    """

    status: str = Field(description="Application status")
    version: str = Field(description="Application version")


class ErrorResponse(BaseModel):
    """Schema for error responses.

    Attributes:
        code: Error code for machine reading.
        message: Human-readable error message.
        details: Optional additional error details.
    """

    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


# ===== Authentication Schemas =====


class UserRegister(BaseModel):
    """Schema for user registration request.

    Attributes:
        email: User email address.
        password: User password (min 8 characters).
        full_name: User's full name (optional).
    """

    email: str = Field(
        ..., min_length=5, max_length=255, description="User email address"
    )
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )
    full_name: Optional[str] = Field(
        None, max_length=255, description="User's full name"
    )


class UserLogin(BaseModel):
    """Schema for user login request.

    Attributes:
        email: User email address.
        password: User password.
    """

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Schema for authentication token response.

    Attributes:
        access_token: JWT access token for API requests.
        refresh_token: JWT refresh token for getting new access tokens.
        token_type: Token type (always "bearer").
        user: User information.
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: Optional[dict] = Field(None, description="User information")


class AccessTokenResponse(BaseModel):
    """Schema for access token response.

    Attributes:
        access_token: New JWT access token.
        token_type: Token type (always "bearer").
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Schema for user data response.

    Attributes:
        id: User ID.
        email: User email.
        username: User username.
        full_name: User's full name.
        role: User role.
        is_active: Whether user account is active.
        email_verified: Whether email is verified.
        created_at: Account creation timestamp.
        updated_at: Last profile update timestamp.
    """

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    email_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class RoleResponse(BaseModel):
    """Schema for role data response.

    Attributes:
        id: Role ID.
        name: Role name (admin, analyst, partner).
        description: Role description.
        level: Role hierarchy level.
        is_active: Whether role is active.
    """

    id: int = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    level: Optional[int] = Field(None, description="Role hierarchy level")
    is_active: bool = Field(..., description="Role active status")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema for password change request.

    Attributes:
        old_password: Current password.
        new_password: New password (min 8 characters).
    """

    old_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request.

    Attributes:
        refresh_token: Valid refresh token.
    """

    refresh_token: str = Field(..., description="Refresh token")


# ===== IC Memo Schemas =====


class ICMemoContentBase(BaseModel):
    """Base schema for IC memo content sections."""

    summary: Optional[str] = Field(None, max_length=5000, description="Executive summary")
    market: Optional[str] = Field(None, max_length=5000, description="Market analysis")
    product: Optional[str] = Field(None, max_length=5000, description="Product description")
    traction: Optional[str] = Field(None, max_length=5000, description="Traction metrics")
    risks: Optional[str] = Field(None, max_length=5000, description="Identified risks")
    open_questions: Optional[str] = Field(None, max_length=5000, description="Open questions")


class ICMemoCreate(ICMemoContentBase):
    """Schema for creating a new IC memo."""

    pass


class ICMemoUpdate(ICMemoContentBase):
    """Schema for updating IC memo.
    
    All fields are optional to support partial updates.
    """

    pass


class ICMemo(ICMemoContentBase):
    """Schema for IC memo response.

    Attributes:
        id: Unique memo identifier.
        deal_id: Associated deal ID.
        created_by: User ID who created the memo.
        last_updated_by: User ID who last updated the memo.
        current_version: Current version number.
        created_at: Timestamp when memo was created.
        updated_at: Timestamp when memo was last updated.
    """

    id: int = Field(..., description="Memo ID")
    deal_id: int = Field(..., description="Deal ID")
    created_by: int = Field(..., description="Creator user ID")
    last_updated_by: int = Field(..., description="Last editor user ID")
    current_version: int = Field(..., description="Current version number")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class ICMemoVersionResponse(ICMemoContentBase):
    """Schema for IC memo version response.

    Attributes:
        id: Unique version record identifier.
        memo_id: Associated memo ID.
        deal_id: Associated deal ID.
        version_number: Version number.
        created_by: User ID who created this version.
        change_summary: Summary of changes in this version.
        created_at: Timestamp when this version was created.
    """

    id: int = Field(..., description="Version record ID")
    memo_id: int = Field(..., description="Memo ID")
    deal_id: int = Field(..., description="Deal ID")
    version_number: int = Field(..., description="Version number")
    created_by: int = Field(..., description="Creator user ID")
    change_summary: Optional[str] = Field(None, description="Change summary")
    created_at: datetime = Field(..., description="Version creation timestamp")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class ICMemoHistoryResponse(BaseModel):
    """Schema for IC memo version history response.

    Attributes:
        total_versions: Total number of versions.
        versions: List of version records.
    """

    total_versions: int = Field(..., description="Total version count")
    versions: list[ICMemoVersionResponse] = Field(..., description="Version records")
