"""API route handlers for Deal Pipeline (Kanban) management.

Routes are organized as methods in handler classes,
following RESTful conventions with proper dependency injection.
Includes endpoints for CRUD operations, stage transitions, and activity logs.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from deals_processor.core.database import get_db_session
from deals_processor.core.security import get_current_user
from deals_processor.core.exceptions import NotFoundError, ValidationError
from deals_processor.models.user import UserModel
from deals_processor.schemas import Deal, DealCreate, DealUpdate, DealStageUpdate, Activity, ErrorResponse
from deals_processor.services.deal_service import DealService

logger = logging.getLogger(__name__)


class DealRouteHandler:
    """Handler class for Deal Pipeline API endpoints.
    
    Organizes all deal routes as methods. Follows OOP principles
    with dependency injection for services and database access.
    Provides Kanban board operations including stage transitions.
    """

    def __init__(self) -> None:
        """Initialize route handler."""
        self.router = APIRouter(prefix="/deals", tags=["deals-pipeline"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup all deal routes."""
        # CRUD operations
        self.router.post(
            "",
            response_model=Deal,
            status_code=status.HTTP_201_CREATED,
            responses={400: {"model": ErrorResponse}},
        )(self.create_deal)

        self.router.get(
            "",
            response_model=list[Deal],
            status_code=status.HTTP_200_OK,
        )(self.list_deals)

        self.router.get(
            "/{deal_id}",
            response_model=Deal,
            status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse}},
        )(self.get_deal)

        self.router.put(
            "/{deal_id}",
            response_model=Deal,
            status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse}},
        )(self.update_deal)

        self.router.delete(
            "/{deal_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            responses={404: {"model": ErrorResponse}},
        )(self.delete_deal)

        # Kanban Pipeline operations
        self.router.post(
            "/{deal_id}/move",
            response_model=dict,
            status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
        )(self.move_deal_stage)

        self.router.get(
            "/stage/{stage}",
            response_model=list[Deal],
            status_code=status.HTTP_200_OK,
        )(self.get_deals_by_stage)

        self.router.get(
            "/owner/{owner}",
            response_model=list[Deal],
            status_code=status.HTTP_200_OK,
        )(self.get_deals_by_owner)

        # Pipeline summary (Kanban view)
        self.router.get(
            "/stats/pipeline-summary",
            response_model=dict,
            status_code=status.HTTP_200_OK,
        )(self.get_pipeline_summary)

        # Activity logs
        self.router.get(
            "/{deal_id}/activities",
            response_model=list[Activity],
            status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse}},
        )(self.get_deal_activities)

    async def create_deal(
        self,
        deal_data: DealCreate,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> dict:
        """Create a new deal in the pipeline (Sourced stage).

        Args:
            deal_data: Deal creation request data.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            dict: Created deal response.
            
        Raises:
            HTTPException: If validation or creation fails.
        """
        try:
            logger.info(f"Deal creation requested by user: {current_user.id}")
            service = DealService(db)
            return service.create_deal(
                name=deal_data.name,
                owner=deal_data.owner,
                company_url=deal_data.company_url,
                stage=deal_data.stage,
                round=deal_data.round,
                check_size=deal_data.check_size,
                status=deal_data.status,
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create deal",
            )

    async def list_deals(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> list[dict]:
        """List all deals with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            list[dict]: List of deals.
        """
        logger.info(f"List deals requested by user: {current_user.id}")
        service = DealService(db)
        return service.list_deals(skip, limit)

    async def get_deal(
        self,
        deal_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> dict:
        """Get a specific deal by ID.

        Args:
            deal_id: Deal ID.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            dict: Deal data.
            
        Raises:
            HTTPException: If deal not found.
        """
        try:
            logger.info(f"Get deal {deal_id} requested by user: {current_user.id}")
            service = DealService(db)
            return service.get_deal(deal_id)
        except NotFoundError as e:
            logger.warning(f"Deal not found: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            )

    async def update_deal(
        self,
        deal_id: int,
        deal_data: DealUpdate,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> dict:
        """Update deal information (without changing stage).

        Args:
            deal_id: Deal ID.
            deal_data: Deal update data.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            dict: Updated deal data.
            
        Raises:
            HTTPException: If deal not found or update fails.
        """
        try:
            logger.info(f"Update deal {deal_id} requested by user: {current_user.id}")
            service = DealService(db)
            return service.update_deal(deal_id, deal_data)
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )

    async def delete_deal(
        self,
        deal_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> None:
        """Delete a deal.

        Args:
            deal_id: Deal ID to delete.
            current_user: Current authenticated user.
            db: Database session.
            
        Raises:
            HTTPException: If deal not found.
        """
        try:
            logger.info(f"Delete deal {deal_id} requested by user: {current_user.id}")
            service = DealService(db)
            if not service.delete_deal(deal_id):
                raise NotFoundError("Deal", deal_id)
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            )

    async def move_deal_stage(
        self,
        deal_id: int,
        stage_data: DealStageUpdate,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> dict:
        """Move a deal to a different pipeline stage (Kanban drag-and-drop).

        Creates an activity log entry recording the stage change with user role.

        Args:
            deal_id: Deal ID to move.
            stage_data: New stage information.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            dict: Updated deal with activity record.
            
        Raises:
            HTTPException: If deal not found or stage transition invalid.
        """
        try:
            # Convert enum to string value if needed
            new_stage = stage_data.stage.value if hasattr(stage_data.stage, 'value') else str(stage_data.stage)
            logger.info(f"Move deal {deal_id} to {new_stage} by {current_user.role} user {current_user.id}")
            service = DealService(db)
            return service.move_deal_to_stage(deal_id, new_stage, current_user.id, current_user.role)
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )

    async def get_deals_by_stage(
        self,
        stage: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> list[dict]:
        """Get all deals in a specific pipeline stage.

        Args:
            stage: Pipeline stage to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            list[dict]: List of deals in the stage.
        """
        logger.info(f"Get deals by stage '{stage}' requested by user: {current_user.id}")
        service = DealService(db)
        return service.get_deals_by_stage(stage, skip, limit)

    async def get_deals_by_owner(
        self,
        owner: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> list[dict]:
        """Get all deals owned by a specific person.

        Args:
            owner: Owner name to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            list[dict]: List of deals owned by the person.
        """
        logger.info(f"Get deals by owner '{owner}' requested by user: {current_user.id}")
        service = DealService(db)
        return service.get_deals_by_owner(owner, skip, limit)

    async def get_pipeline_summary(
        self,
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> dict:
        """Get Kanban board summary (count of deals in each stage).

        Returns pipeline statistics for the Kanban board visualization.

        Args:
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            dict: Count of deals per stage.
        """
        logger.info(f"Get pipeline summary requested by user: {current_user.id}")
        service = DealService(db)
        return service.get_pipeline_summary()

    async def get_deal_activities(
        self,
        deal_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=500),
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ) -> list[dict]:
        """Get activity log for a specific deal.

        Returns all activities including stage changes with timestamps.

        Args:
            deal_id: Deal ID to get activities for.
            skip: Number of records to skip.
            limit: Maximum records to return.
            current_user: Current authenticated user.
            db: Database session.
            
        Returns:
            list[dict]: List of activities for the deal.
            
        Raises:
            HTTPException: If deal not found.
        """
        try:
            logger.info(f"Get activities for deal {deal_id} requested by user: {current_user.id}")
            service = DealService(db)
            return service.get_deal_activities(deal_id, skip, limit)
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message,
            )


# Create route handler instance for Kanban Deal Pipeline
deal_handler = DealRouteHandler()
router = deal_handler.router
