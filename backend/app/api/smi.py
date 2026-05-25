from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.smi import SMIService
from ..models.pydantic_models import (
    SMIRequestCreate, 
    SMIRequestResponse,
    MessageResponse
)

router = APIRouter(prefix="/smi", tags=["SMI"])


@router.post("/analyze", response_model=MessageResponse)
async def analyze_topic(
    request: SMIRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    """Analyze topic relevance and viral potential"""
    service = SMIService(db)
    
    topic = request.topic or ""
    
    result = await service.analyze_topic(
        topic=topic,
        user_id=current_user_id,
        keywords=request.keywords
    )
    
    return MessageResponse(
        message="Анализ темы успешно выполнен",
        data=result
    )


@router.get("/requests/{request_id}", response_model=SMIRequestResponse)
async def get_smi_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get SMI request by ID"""
    service = SMIService(db)
    request = service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return SMIRequestResponse.model_validate(request)


@router.get("/requests", response_model=List[SMIRequestResponse])
async def get_user_smi_requests(
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
    limit: int = 10
):
    """Get all SMI requests for current user"""
    service = SMIService(db)
    requests = service.get_user_requests(current_user_id, limit)
    
    return [SMIRequestResponse.model_validate(r) for r in requests]
