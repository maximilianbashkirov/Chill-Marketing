from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.help_colleague import HelpColleagueService
from ..models.pydantic_models import (
    HelpColleaguePostCreate,
    HelpColleaguePostResponse,
    HelpColleagueResponseCreate,
    HelpColleagueResponseResponse,
    HelpColleagueTagResponse,
    HelpColleagueProfileResponse,
    HelpColleagueNotificationResponse,
    MessageResponse,
)

router = APIRouter(prefix="/help-colleague", tags=["Help Colleague"])

# ─── Tags ──────────────────────────────────────────────────────

@router.get("/tags", response_model=List[HelpColleagueTagResponse])
async def get_tags(db: Session = Depends(get_db)):
    service = HelpColleagueService(db)
    return service.get_all_tags()


@router.post("/tags", response_model=HelpColleagueTagResponse)
async def create_tag(name: str, category: str = "general", db: Session = Depends(get_db)):
    service = HelpColleagueService(db)
    tag = service._ensure_tags([name])
    return tag[0] if tag else None

# ─── Posts ─────────────────────────────────────────────────────

@router.post("/posts", response_model=HelpColleaguePostResponse)
async def create_post(
    post: HelpColleaguePostCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    created_post = service.create_post(
        title=post.title or "",
        description=post.description or post.content or "",
        category=post.category,
        user_id=current_user_id,
        is_anonymous=post.is_anonymous,
        tags=post.tags,
    )
    return HelpColleaguePostResponse.model_validate(created_post)


@router.get("/posts", response_model=List[HelpColleaguePostResponse])
async def get_posts(
    category: Optional[str] = None,
    sort: str = Query("new", regex="^(new|hot|top)$"),
    tag: Optional[List[str]] = Query(None),
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    posts = service.get_all_posts(
        category=category,
        sort=sort,
        tags=tag,
        page=page,
        limit=limit,
    )
    return [HelpColleaguePostResponse.model_validate(p) for p in posts]


@router.get("/posts/top", response_model=List[HelpColleaguePostResponse])
async def get_top_posts(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    posts = service.get_top_posts(limit=limit)
    return [HelpColleaguePostResponse.model_validate(p) for p in posts]


@router.get("/posts/hot", response_model=List[HelpColleaguePostResponse])
async def get_hot_posts(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    posts = service.get_hot_posts(limit=limit)
    return [HelpColleaguePostResponse.model_validate(p) for p in posts]


@router.get("/posts/{post_id}", response_model=HelpColleaguePostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    post = service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return HelpColleaguePostResponse.model_validate(post)


@router.get("/posts/{post_id}/responses", response_model=List[HelpColleagueResponseResponse])
async def get_post_responses(
    post_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    responses = service.get_post_responses(post_id, limit=limit)
    return [HelpColleagueResponseResponse.model_validate(r) for r in responses]


@router.post("/posts/{post_id}/responses", response_model=HelpColleagueResponseResponse)
async def create_response(
    post_id: int,
    response: HelpColleagueResponseCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    created_response = service.create_response(
        post_id=post_id,
        user_id=current_user_id,
        content=response.content,
        rating=response.rating,
    )
    return HelpColleagueResponseResponse.model_validate(created_response)


@router.post("/posts/{post_id}/ai-response", response_model=MessageResponse)
async def generate_ai_response(
    post_id: int,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    post = service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    ai_response_text = await service.generate_ai_response(post)
    ai_response = service.create_response(
        post_id=post_id,
        user_id=0,
        content=ai_response_text,
        is_from_bot=True,
    )

    return MessageResponse(
        message="AI ответ успешно сгенерирован",
        data=HelpColleagueResponseResponse.model_validate(ai_response),
    )


@router.post("/posts/{post_id}/vote", response_model=HelpColleaguePostResponse)
async def vote_post(
    post_id: int,
    vote: int = Query(..., description="1 or -1"),
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    updated_post = service.vote_post(post_id, current_user_id, vote)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return HelpColleaguePostResponse.model_validate(updated_post)


@router.post("/posts/{post_id}/close", response_model=HelpColleaguePostResponse)
async def close_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    updated_post = service.close_post(post_id, current_user_id)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only post owner can close the post"
        )
    return HelpColleaguePostResponse.model_validate(updated_post)

# ─── Responses ─────────────────────────────────────────────────

@router.post("/responses/{response_id}/rate", response_model=HelpColleagueResponseResponse)
async def rate_response(
    response_id: int,
    rating: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    updated_response = service.rate_response(response_id, current_user_id, rating)
    if not updated_response:
        raise HTTPException(status_code=404, detail="Response not found")
    return HelpColleagueResponseResponse.model_validate(updated_response)

# ─── Search ────────────────────────────────────────────────────

@router.get("/search", response_model=List[HelpColleaguePostResponse])
async def search_posts(
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    posts = service.search_posts(q, limit=limit)
    return [HelpColleaguePostResponse.model_validate(p) for p in posts]

# ─── Profile ───────────────────────────────────────────────────

@router.get("/profile/{user_id}", response_model=HelpColleagueProfileResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    profile = service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@router.get("/profile/{user_id}/posts", response_model=List[HelpColleaguePostResponse])
async def get_user_posts(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    posts = service.get_user_posts(user_id, limit=limit)
    return [HelpColleaguePostResponse.model_validate(p) for p in posts]


@router.get("/profile/{user_id}/responses", response_model=List[HelpColleagueResponseResponse])
async def get_user_responses(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    service = HelpColleagueService(db)
    responses = service.get_user_responses(user_id, limit=limit)
    return [HelpColleagueResponseResponse.model_validate(r) for r in responses]

# ─── Notifications ─────────────────────────────────────────────

@router.get("/notifications", response_model=List[HelpColleagueNotificationResponse])
async def get_notifications(
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    notifs = service.get_notifications(current_user_id)
    return notifs


@router.get("/notifications/unread-count", response_model=dict)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    count = service.get_unread_notification_count(current_user_id)
    return {"count": count}


@router.post("/notifications/read", response_model=MessageResponse)
async def mark_notifications_read(
    db: Session = Depends(get_db),
    current_user_id: int = 1
):
    service = HelpColleagueService(db)
    service.mark_notifications_read(current_user_id)
    return MessageResponse(message="Уведомления отмечены как прочитанные")
