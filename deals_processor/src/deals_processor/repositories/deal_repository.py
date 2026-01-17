"""Repository classes implementing data access layer with OOP principles.

Repositories provide abstraction over database operations and enable
easy switching between different data sources.
"""

import logging
from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from deals_processor.models.deal import BaseModel, DealModel, ActivityModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Generic base repository with common CRUD operations.
    
    Implements Repository Pattern to abstract data access logic.
    Uses generics for type-safe database operations.
    """

    def __init__(self, db_session: Session, model_class: Type[T]) -> None:
        """Initialize repository with database session and model class.
        
        Args:
            db_session: SQLAlchemy database session.
            model_class: Model class this repository manages.
        """
        self.db = db_session
        self.model = model_class
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, **kwargs) -> T:
        """Create and persist a new entity.
        
        Args:
            **kwargs: Entity attributes.
            
        Returns:
            T: Created entity instance.
        """
        entity = self.model(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        self.logger.info(f"Created {self.model.__name__} with id={entity.id}")
        return entity

    def read(self, entity_id: int) -> Optional[T]:
        """Read entity by ID.
        
        Args:
            entity_id: Entity ID.
            
        Returns:
            Optional[T]: Entity instance or None if not found.
        """
        entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if entity:
            self.logger.debug(f"Retrieved {self.model.__name__} with id={entity_id}")
        else:
            self.logger.warning(f"{self.model.__name__} with id={entity_id} not found")
        return entity

    def read_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Read all entities with pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            
        Returns:
            list[T]: List of entity instances.
        """
        entities = (
            self.db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )
        self.logger.debug(f"Retrieved {len(entities)} {self.model.__name__} records")
        return entities

    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """Update an existing entity.
        
        Args:
            entity_id: Entity ID.
            **kwargs: Attributes to update.
            
        Returns:
            Optional[T]: Updated entity or None if not found.
        """
        entity = self.read(entity_id)
        if not entity:
            return None

        for key, value in kwargs.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)

        self.db.commit()
        self.db.refresh(entity)
        self.logger.info(f"Updated {self.model.__name__} with id={entity_id}")
        return entity

    def delete(self, entity_id: int) -> bool:
        """Delete an entity.
        
        Args:
            entity_id: Entity ID.
            
        Returns:
            bool: True if deleted, False if not found.
        """
        entity = self.read(entity_id)
        if not entity:
            return False

        self.db.delete(entity)
        self.db.commit()
        self.logger.info(f"Deleted {self.model.__name__} with id={entity_id}")
        return True

    def count(self) -> int:
        """Count total entities.
        
        Returns:
            int: Total number of entities.
        """
        return self.db.query(self.model).count()


class DealRepository(BaseRepository[DealModel]):
    """Deal-specific repository with custom queries for Kanban pipeline.
    
    Extends BaseRepository with deal-specific business logic including
    stage-based filtering and pipeline summary queries.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize DealRepository.
        
        Args:
            db_session: SQLAlchemy database session.
        """
        super().__init__(db_session, DealModel)

    def find_by_stage(self, stage: str, skip: int = 0, limit: int = 100) -> list[DealModel]:
        """Find all deals in a specific pipeline stage.

        Args:
            stage: Pipeline stage to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[DealModel]: List of deals in the specified stage.
        """
        try:
            deals = self.db.query(self.model).filter(
                self.model.stage == stage
            ).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(deals)} deals in stage: {stage}")
            return deals
        except Exception as e:
            self.logger.error(f"Error finding deals by stage: {e}")
            return []

    def find_by_owner(self, owner: str, skip: int = 0, limit: int = 100) -> list[DealModel]:
        """Find all deals owned by a specific person.

        Args:
            owner: Owner name to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[DealModel]: List of deals owned by the person.
        """
        try:
            deals = self.db.query(self.model).filter(
                self.model.owner == owner
            ).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(deals)} deals owned by: {owner}")
            return deals
        except Exception as e:
            self.logger.error(f"Error finding deals by owner: {e}")
            return []

    def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> list[DealModel]:
        """Find deals by status.
        
        Args:
            status: Deal status to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.
            
        Returns:
            list[DealModel]: Deals with matching status.
        """
        deals = (
            self.db.query(DealModel)
            .filter(DealModel.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )
        self.logger.debug(f"Found {len(deals)} deals with status={status}")
        return deals

    def find_by_name(self, name: str) -> Optional[DealModel]:
        """Find deal by exact name match.
        
        Args:
            name: Deal name to search for.
            
        Returns:
            Optional[DealModel]: Deal if found, None otherwise.
        """
        deal = self.db.query(DealModel).filter(DealModel.name == name).first()
        if deal:
            self.logger.debug(f"Found deal with name={name}")
        return deal

    def count_by_stage(self, stage: str) -> int:
        """Count deals in a specific stage.

        Args:
            stage: Pipeline stage to count.

        Returns:
            int: Number of deals in the stage.
        """
        try:
            count = self.db.query(self.model).filter(
                self.model.stage == stage
            ).count()
            self.logger.debug(f"Counted {count} deals in stage: {stage}")
            return count
        except Exception as e:
            self.logger.error(f"Error counting deals by stage: {e}")
            return 0

    def count_by_status(self, status: str) -> int:
        """Count deals by status.
        
        Args:
            status: Deal status to count.
            
        Returns:
            int: Number of deals with given status.
        """
        count = self.db.query(DealModel).filter(DealModel.status == status).count()
        self.logger.debug(f"Found {count} deals with status={status}")
        return count

    def get_pipeline_summary(self) -> dict:
        """Get summary of deals in each pipeline stage.

        Returns:
            dict: Count of deals per stage.
        """
        try:
            stages = ["Sourced", "Screen", "Diligence", "IC", "Invested", "Passed"]
            summary = {}
            for stage in stages:
                count = self.count_by_stage(stage)
                summary[stage] = count
            self.logger.debug(f"Pipeline summary: {summary}")
            return summary
        except Exception as e:
            self.logger.error(f"Error getting pipeline summary: {e}")
            return {}


class ActivityRepository(BaseRepository[ActivityModel]):
    """Repository for Activity model data access.

    Handles activity logging and retrieval for deal pipeline auditing.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize activity repository.

        Args:
            db_session: SQLAlchemy database session.
        """
        super().__init__(db_session, ActivityModel)
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_by_deal(self, deal_id: int, skip: int = 0, limit: int = 50) -> list[ActivityModel]:
        """Find all activities related to a specific deal.

        Args:
            deal_id: Deal ID to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[ActivityModel]: List of activities for the deal.
        """
        try:
            activities = self.db.query(self.model).filter(
                self.model.deal_id == deal_id
            ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(activities)} activities for deal: {deal_id}")
            return activities
        except Exception as e:
            self.logger.error(f"Error finding activities by deal: {e}")
            return []

    def find_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[ActivityModel]:
        """Find all activities performed by a specific user.

        Args:
            user_id: User ID to filter by.
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[ActivityModel]: List of activities by the user.
        """
        try:
            activities = self.db.query(self.model).filter(
                self.model.user_id == user_id
            ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(activities)} activities by user: {user_id}")
            return activities
        except Exception as e:
            self.logger.error(f"Error finding activities by user: {e}")
            return []

    def find_by_type(self, activity_type: str, skip: int = 0, limit: int = 50) -> list[ActivityModel]:
        """Find all activities of a specific type.

        Args:
            activity_type: Activity type to filter by (e.g., "stage_change").
            skip: Number of records to skip (pagination).
            limit: Maximum records to return.

        Returns:
            list[ActivityModel]: List of activities of the specified type.
        """
        try:
            activities = self.db.query(self.model).filter(
                self.model.activity_type == activity_type
            ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
            self.logger.debug(f"Found {len(activities)} activities of type: {activity_type}")
            return activities
        except Exception as e:
            self.logger.error(f"Error finding activities by type: {e}")
            return []
