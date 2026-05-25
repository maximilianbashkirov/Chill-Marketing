from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.analytics import AnalyticsService
from ..models.pydantic_models import (
    AnalyticsRequestCreate, 
    AnalyticsRequestResponse,
    MessageResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/analyze", response_model=MessageResponse)
async def analyze_idea(
    request: AnalyticsRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Replace with actual auth
):
    """Analyze a marketing idea"""
    service = AnalyticsService(db)
    
    result = await service.analyze_idea(
        idea_description=request.idea_description,
        user_id=current_user_id,
        analysis_type=request.analysis_type
    )
    
    return MessageResponse(
        message="Анализ успешно выполнен",
        data=result
    )


@router.get("/requests/{request_id}", response_model=AnalyticsRequestResponse)
async def get_analytics_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get analytics request by ID"""
    service = AnalyticsService(db)
    request = service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return AnalyticsRequestResponse.model_validate(request)


@router.get("/requests", response_model=List[AnalyticsRequestResponse])
async def get_user_analytics_requests(
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
    limit: int = 10
):
    """Get all analytics requests for current user"""
    service = AnalyticsService(db)
    requests = service.get_user_requests(current_user_id, limit)
    
    return [AnalyticsRequestResponse.model_validate(r) for r in requests]
