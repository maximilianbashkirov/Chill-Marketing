from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.market_research import MarketResearchService
from ..models.pydantic_models import (
    MarketResearchRequestCreate, 
    MarketResearchRequestResponse,
    MessageResponse
)

router = APIRouter(prefix="/market-research", tags=["Market Research"])


@router.post("/conduct", response_model=MessageResponse)
async def conduct_research(
    request: MarketResearchRequestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    """Conduct market research with statistics and cases"""
    service = MarketResearchService(db)
    
    # Извлекаем требования из запроса, если они были предоставлены
    # Поскольку Pydantic модель MarketResearchRequestCreate не включает требования,
    # мы проверяем, есть ли они в исходном запросе через дополнительную обработку
    # Но для простоты и совместимости, будем использовать только topic и industry
    # Дополнительные требования можно будет добавить в будущих версиях API
    
    result = await service.conduct_research(
        topic=request.topic or "",
        user_id=current_user_id,
        industry=request.industry,
        requirements=request.requirements
    )
    
    return MessageResponse(
        message="Исследование рынка успешно выполнено",
        data=result
    )


@router.get("/requests/{request_id}", response_model=MarketResearchRequestResponse)
async def get_research_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Get market research request by ID"""
    service = MarketResearchService(db)
    request = service.get_request_by_id(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return MarketResearchRequestResponse.model_validate(request)


@router.get("/requests", response_model=List[MarketResearchRequestResponse])
async def get_user_research_requests(
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # TODO: Replace with actual auth
    limit: int = 10
):
    """Get all market research requests for current user"""
    service = MarketResearchService(db)
    requests = service.get_user_requests(current_user_id, limit)
    
    return [MarketResearchRequestResponse.model_validate(r) for r in requests]
