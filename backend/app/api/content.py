from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.content import ContentService
from ..models.pydantic_models import (
    ContentRequestCreate, 
    ContentRequestResponse,
    MessageResponse
)

router = APIRouter(prefix="/content", tags=["Content"])


@router.post("/analyze", response_model=MessageResponse)
async def analyze_content_idea(
    request: ContentRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    """Analyze a content idea (post/reel/podcast/article)"""
    service = ContentService(db)
    
    result = await service.analyze_content_idea(
        content_type=request.content_type or "post",
        idea_description=request.content_idea,
        user_id=current_user_id,
        target_audience=request.target_audience,
        platform=request.platform
    )
    
    return MessageResponse(
        message="Анализ контента успешно выполнен",
        data=result
    )


@router.get("/requests/{request_id}", response_model=ContentRequestResponse)
async def get_content_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get content request by ID"""
    service = ContentService(db)
    request = service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return ContentRequestResponse.model_validate(request)


@router.get("/requests", response_model=List[ContentRequestResponse])
async def get_user_content_requests(
    db: Session = Depends(get_db),
    current_user_id: int = 1,
    limit: int = 10
):
    """Get all content requests for current user"""
    service = ContentService(db)
    requests = service.get_user_requests(current_user_id, limit)
    
    return [ContentRequestResponse.model_validate(r) for r in requests]
