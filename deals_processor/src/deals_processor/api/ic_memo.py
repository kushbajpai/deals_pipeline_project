"""IC Memo API endpoints for deal evaluation and versioning."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from deals_processor.core.database import get_db_session
from deals_processor.core.security import get_current_user
from deals_processor.models.deal import DealModel
from deals_processor.models.ic_memo import ICMemoModel, ICMemoVersionModel
from deals_processor.models.user import UserModel
from deals_processor.schemas import (
    ICMemo,
    ICMemoCreate,
    ICMemoHistoryResponse,
    ICMemoUpdate,
    ICMemoVersionResponse,
)

router = APIRouter(prefix="/deals", tags=["IC Memo"])


@router.post("/{deal_id}/memos", response_model=ICMemo, status_code=status.HTTP_201_CREATED)
def create_or_update_memo(
    deal_id: int,
    memo_data: ICMemoCreate,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """Create a new IC memo or update existing memo for a deal.
    
    Creates a new version on each save. All previous versions are preserved
    in the version history table.
    
    Args:
        deal_id: Deal ID.
        memo_data: Memo content and sections.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        Created/updated memo with current version number.
        
    Raises:
        HTTPException: If deal not found or user not authorized.
    """
    # Verify deal exists
    deal = db.query(DealModel).filter(DealModel.id == deal_id).first()
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with ID {deal_id} not found",
        )

    # Check if memo exists for this deal
    memo = db.query(ICMemoModel).filter(ICMemoModel.deal_id == deal_id).first()

    if memo:
        # Create version snapshot of current memo before updating
        old_version = ICMemoVersionModel(
            memo_id=memo.id,
            deal_id=deal_id,
            version_number=memo.current_version,
            created_by=memo.last_updated_by,
            summary=memo.summary,
            market=memo.market,
            product=memo.product,
            traction=memo.traction,
            risks=memo.risks,
            open_questions=memo.open_questions,
            change_summary="Previous version",
        )
        db.add(old_version)
        db.flush()

        # Update memo with new content
        memo.summary = memo_data.summary
        memo.market = memo_data.market
        memo.product = memo_data.product
        memo.traction = memo_data.traction
        memo.risks = memo_data.risks
        memo.open_questions = memo_data.open_questions
        memo.last_updated_by = current_user.id
        memo.current_version += 1

        db.commit()
        db.refresh(memo)
        return memo

    else:
        # Create new memo
        memo = ICMemoModel(
            deal_id=deal_id,
            created_by=current_user.id,
            last_updated_by=current_user.id,
            current_version=1,
            summary=memo_data.summary,
            market=memo_data.market,
            product=memo_data.product,
            traction=memo_data.traction,
            risks=memo_data.risks,
            open_questions=memo_data.open_questions,
        )
        db.add(memo)
        db.commit()
        db.refresh(memo)

        # Create initial version record
        version = ICMemoVersionModel(
            memo_id=memo.id,
            deal_id=deal_id,
            version_number=1,
            created_by=current_user.id,
            summary=memo_data.summary,
            market=memo_data.market,
            product=memo_data.product,
            traction=memo_data.traction,
            risks=memo_data.risks,
            open_questions=memo_data.open_questions,
            change_summary="Initial version",
        )
        db.add(version)
        db.commit()

        return memo


@router.get("/{deal_id}/memos", response_model=ICMemo)
def get_memo(
    deal_id: int,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """Get current IC memo for a deal.
    
    Returns the latest version of the IC memo.
    
    Args:
        deal_id: Deal ID.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        Current memo with latest version number.
        
    Raises:
        HTTPException: If deal or memo not found.
    """
    # Verify deal exists
    deal = db.query(DealModel).filter(DealModel.id == deal_id).first()
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with ID {deal_id} not found",
        )

    memo = db.query(ICMemoModel).filter(ICMemoModel.deal_id == deal_id).first()
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No IC memo found for deal {deal_id}",
        )

    return memo


@router.get("/{deal_id}/memos/versions", response_model=ICMemoHistoryResponse)
def get_memo_history(
    deal_id: int,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """Get version history for a deal's IC memo.
    
    Returns all versions of the IC memo in reverse chronological order
    (latest first).
    
    Args:
        deal_id: Deal ID.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        List of all memo versions with metadata.
        
    Raises:
        HTTPException: If deal or memo not found.
    """
    # Verify deal exists
    deal = db.query(DealModel).filter(DealModel.id == deal_id).first()
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with ID {deal_id} not found",
        )

    # Check if memo exists
    memo = db.query(ICMemoModel).filter(ICMemoModel.deal_id == deal_id).first()
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No IC memo found for deal {deal_id}",
        )

    versions = (
        db.query(ICMemoVersionModel)
        .filter(ICMemoVersionModel.memo_id == memo.id)
        .order_by(ICMemoVersionModel.version_number.desc())
        .all()
    )

    return {
        "total_versions": len(versions),
        "versions": versions,
    }


@router.get("/{deal_id}/memos/versions/{version_num}", response_model=ICMemoVersionResponse)
def get_memo_version(
    deal_id: int,
    version_num: int,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
) -> dict:
    """Get a specific version of an IC memo.
    
    Returns a read-only snapshot of the memo at a specific version number.
    
    Args:
        deal_id: Deal ID.
        version_num: Version number to retrieve.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        Memo version snapshot.
        
    Raises:
        HTTPException: If deal, memo, or version not found.
    """
    # Verify deal exists
    deal = db.query(DealModel).filter(DealModel.id == deal_id).first()
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with ID {deal_id} not found",
        )

    # Check if memo exists
    memo = db.query(ICMemoModel).filter(ICMemoModel.deal_id == deal_id).first()
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No IC memo found for deal {deal_id}",
        )

    # Get specific version
    version = (
        db.query(ICMemoVersionModel)
        .filter(
            ICMemoVersionModel.memo_id == memo.id,
            ICMemoVersionModel.version_number == version_num,
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_num} not found for memo {memo.id}",
        )

    return version
