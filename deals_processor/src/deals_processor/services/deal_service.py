"""Service layer implementing business logic for deal management.

Services orchestrate repository operations and implement business rules.
Handles deal pipeline operations, stage transitions, and activity logging.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from deals_processor.core.exceptions import ValidationError, NotFoundError
from deals_processor.core.config import get_settings
from deals_processor.models.deal import DealModel, ActivityModel
from deals_processor.repositories.deal_repository import DealRepository, ActivityRepository
from deals_processor.schemas import DealCreate, DealUpdate

logger = logging.getLogger(__name__)


class DealService:
    """Service class for deal business logic and Kanban pipeline management.
    
    Orchestrates repository operations and implements deal-related business rules.
    Handles stage transitions with automatic activity logging.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize DealService.
        
        Args:
            db_session: SQLAlchemy database session.
        """
        self.db_session = db_session
        self.deal_repo = DealRepository(db_session)
        self.activity_repo = ActivityRepository(db_session)
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_deal(
        self,
        name: str,
        owner: str,
        company_url: Optional[str] = None,
        stage: str = "Sourced",
        round: Optional[str] = None,
        check_size: Optional[float] = None,
        status: str = "active",
    ) -> dict:
        """Create a new deal in the pipeline.

        Args:
            name: Deal name/title.
            owner: Deal owner/analyst.
            company_url: Company website URL.
            stage: Pipeline stage (default: Sourced).
            round: Investment round.
            check_size: Investment amount.
            status: Deal status (default: active).

        Returns:
            dict: Created deal data.

        Raises:
            ValidationError: If validation fails.
        """
        if not name or not owner:
            raise ValidationError("Name and owner are required")

        try:
            deal = self.deal_repo.create(
                name=name,
                owner=owner,
                company_url=company_url,
                stage=stage,
                round=round,
                check_size=check_size,
                status=status,
            )
            self.logger.info(f"Deal created: {name} (ID: {deal.id})")
            return deal.to_dict()
        except Exception as e:
            self.logger.error(f"Error creating deal: {e}")
            raise ValidationError("Failed to create deal")

    def get_deal(self, deal_id: int) -> dict:
        """Get a deal by ID.
        
        Args:
            deal_id: Deal ID.
            
        Returns:
            dict: Deal data.
            
        Raises:
            NotFoundError: If deal not found.
        """
        deal = self.deal_repo.read(deal_id)
        if not deal:
            raise NotFoundError("Deal", deal_id)
        return deal.to_dict()

    def list_deals(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """List all deals with pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            
        Returns:
            list[dict]: List of deal data.
        """
        deals = self.deal_repo.read_all(skip, limit)
        self.logger.debug(f"Listed {len(deals)} deals")
        return [deal.to_dict() for deal in deals]

    def update_deal(self, deal_id: int, deal_data: DealUpdate) -> dict:
        """Update deal information (without stage change).
        
        Args:
            deal_id: Deal ID.
            deal_data: Deal update data.
            
        Returns:
            dict: Updated deal data.
            
        Raises:
            NotFoundError: If deal not found.
        """
        deal = self.deal_repo.read(deal_id)
        if not deal:
            raise NotFoundError("Deal", deal_id)

        update_kwargs = deal_data.model_dump(exclude_unset=True)
        # Don't allow stage update through this method (use move_deal_to_stage instead)
        update_kwargs.pop("stage", None)

        updated_deal = self.deal_repo.update(deal_id, **update_kwargs)
        self.logger.info(f"Updated deal {deal_id}")
        return updated_deal.to_dict()

    def delete_deal(self, deal_id: int) -> bool:
        """Delete a deal.
        
        Args:
            deal_id: Deal ID.
            
        Returns:
            bool: True if deleted, False if not found.
        """
        deleted = self.deal_repo.delete(deal_id)
        if deleted:
            self.logger.info(f"Deleted deal {deal_id}")
        else:
            self.logger.warning(f"Deal {deal_id} not found for deletion")
        return deleted

    def list_deals_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """List deals by status.
        
        Args:
            status: Deal status filter.
            skip: Number of records to skip.
            limit: Maximum records to return.
            
        Returns:
            list[dict]: List of deal data with matching status.
        """
        deals = self.deal_repo.find_by_status(status, skip, limit)
        self.logger.debug(f"Listed {len(deals)} deals with status={status}")
        return [deal.to_dict() for deal in deals]

    def move_deal_to_stage(
        self,
        deal_id: int,
        new_stage: str,
        user_id: int,
        user_role: str = "user",
    ) -> dict:
        """Move a deal to a new pipeline stage with activity logging.

        Creates an activity log entry for the stage change with user role information.

        Args:
            deal_id: Deal ID to move.
            new_stage: New pipeline stage.
            user_id: User performing the action.
            user_role: Role of the user (e.g., "analyst", "admin").

        Returns:
            dict: Updated deal data including activity record.

        Raises:
            NotFoundError: If deal not found.
            ValidationError: If stage transition invalid.
        """
        deal = self.deal_repo.read(deal_id)
        if not deal:
            raise NotFoundError("Deal", deal_id)

        valid_stages = ["Sourced", "Screen", "Diligence", "IC", "Invested", "Passed"]
        if new_stage not in valid_stages:
            raise ValidationError(f"Invalid stage: {new_stage}")

        if deal.stage == new_stage:
            raise ValidationError("Deal is already in this stage")

        old_stage = deal.stage
        try:
            # Update deal stage
            updated_deal = self.deal_repo.update(deal_id, stage=new_stage)

            # Create activity log with user role and deal name
            role_label = user_role.capitalize() if user_role else "User"
            description = f"{role_label} moved {deal.name} from {old_stage} to {new_stage}"
            activity = self.activity_repo.create(
                deal_id=deal_id,
                user_id=user_id,
                activity_type="stage_change",
                description=description,
                old_value=old_stage,
                new_value=new_stage,
            )

            self.logger.info(f"Deal {deal_id} ({deal.name}) moved from {old_stage} to {new_stage} by {role_label} (user {user_id})")
            return {
                "deal": updated_deal.to_dict(),
                "activity": activity.to_dict(),
            }

        except Exception as e:
            self.logger.error(f"Error moving deal to stage: {e}")
            raise ValidationError("Failed to move deal")

    def get_deals_by_stage(self, stage: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all deals in a specific pipeline stage.

        Args:
            stage: Pipeline stage to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[dict]: List of deals in the stage.
        """
        deals = self.deal_repo.find_by_stage(stage, skip, limit)
        return [deal.to_dict() for deal in deals]

    def get_deals_by_owner(self, owner: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all deals owned by a specific person.

        Args:
            owner: Owner name to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[dict]: List of deals owned by the person.
        """
        deals = self.deal_repo.find_by_owner(owner, skip, limit)
        return [deal.to_dict() for deal in deals]

    def get_pipeline_summary(self) -> dict:
        """Get count of deals in each pipeline stage (Kanban summary).

        Returns:
            dict: Count of deals per stage.
        """
        return self.deal_repo.get_pipeline_summary()

    def get_deal_activities(self, deal_id: int, skip: int = 0, limit: int = 50) -> list[dict]:
        """Get activity history for a deal.

        Args:
            deal_id: Deal ID to get activities for.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[dict]: List of activities for the deal.
            
        Raises:
            NotFoundError: If deal not found.
        """
        # Verify deal exists
        deal = self.deal_repo.read(deal_id)
        if not deal:
            raise NotFoundError("Deal", deal_id)

        activities = self.activity_repo.find_by_deal(deal_id, skip, limit)
        return [activity.to_dict() for activity in activities]

    def get_status_count(self, status: str) -> int:
        """Get count of deals by status.
        
        Args:
            status: Deal status.
            
        Returns:
            int: Number of deals with given status.
        """
        return self.deal_repo.count_by_status(status)

    def get_stage_count(self, stage: str) -> int:
        """Get count of deals in a pipeline stage.
        
        Args:
            stage: Pipeline stage.
            
        Returns:
            int: Number of deals in the stage.
        """
        return self.deal_repo.count_by_stage(stage)

    def get_total_count(self) -> int:
        """Get total number of deals.
        
        Returns:
            int: Total deal count.
        """
        return self.deal_repo.count()
