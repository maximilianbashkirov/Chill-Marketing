from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.dot_analysis import DotAnalysisService
from ..models.pydantic_models import (
    DotAnalysisRequestCreate, 
    DotAnalysisRequestResponse,
    MessageResponse
)

router = APIRouter(prefix="/dot-analysis", tags=["Dot Analysis"])


@router.post("/analyze", response_model=MessageResponse)
async def analyze_case(
    request: DotAnalysisRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    """Analyze case and select best-fit marketing models"""
    service = DotAnalysisService(db)
    
    result = await service.analyze_case(
        case_context=request.case_context_text,
        industry=request.industry or "",
        user_id=current_user_id
    )
    
    return MessageResponse(
        message="Анализ маркетинговых моделей успешно выполнен",
        data=result
    )


@router.get("/requests/{request_id}", response_model=DotAnalysisRequestResponse)
async def get_dot_analysis_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get dot analysis request by ID"""
    service = DotAnalysisService(db)
    request = service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return DotAnalysisRequestResponse.model_validate(request)


@router.get("/requests", response_model=List[DotAnalysisRequestResponse])
async def get_user_dot_analysis_requests(
    db: Session = Depends(get_db),
    current_user_id: int = 1,
    limit: int = 10
):
    """Get all dot analysis requests for current user"""
    service = DotAnalysisService(db)
    requests = service.get_user_requests(current_user_id, limit)
    
    return [DotAnalysisRequestResponse.model_validate(r) for r in requests]


@router.get("/models", response_model=List)
async def get_all_marketing_models(
    db: Session = Depends(get_db)
):
    """Get all available marketing models"""
    service = DotAnalysisService(db)
    return service.get_all_models()
