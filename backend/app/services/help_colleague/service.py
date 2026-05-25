from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from datetime import datetime, timezone
from ...models.models import (
    HelpColleaguePost, HelpColleagueResponse, HelpColleagueTag,
    HelpColleaguePostTag, HelpColleagueNotification, HelpColleagueRatingHistory,
    User
)
from ...utils.llm_client import llm_client


class HelpColleagueService:
    """Service for community idea exchange and evaluation"""

    SYSTEM_PROMPT = """Ты — опытный маркетинг-консультант и ментор.
Твоя задача — помогать коллегам с их идеями, проблемами и вопросами.
Давай конкретные, практические советы. Будь поддерживающим, но честным.
Отвечай на русском языке."""

    def __init__(self, db: Session):
        self.db = db

    # ─── Tags ─────────────────────────────────────────────────

    def _ensure_tags(self, tag_names: List[str]) -> List[HelpColleagueTag]:
        """Get or create tags by name"""
        tags = []
        for name in tag_names:
            name = name.strip().lower()
            if not name:
                continue
            tag = self.db.query(HelpColleagueTag).filter(
                HelpColleagueTag.name == name
            ).first()
            if not tag:
                tag = HelpColleagueTag(name=name)
                self.db.add(tag)
                self.db.flush()
            tags.append(tag)
        return tags

    def get_all_tags(self) -> List[HelpColleagueTag]:
        return self.db.query(HelpColleagueTag).order_by(HelpColleagueTag.name).all()

    # ─── Posts ─────────────────────────────────────────────────

    def create_post(
        self,
        title: str,
        description: str,
        category: str,
        user_id: int,
        is_anonymous: bool = True,
        tags: Optional[List[str]] = None
    ) -> HelpColleaguePost:
        """Create a new post for community discussion"""
        post = HelpColleaguePost(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            is_anonymous=is_anonymous
        )
        self.db.add(post)
        self.db.flush()

        if tags:
            post.tags = self._ensure_tags(tags)

        self.db.commit()
        self.db.refresh(post)
        return post

    def get_post_by_id(self, post_id: int) -> Optional[HelpColleaguePost]:
        """Get post by ID with tags"""
        return self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        ).filter(HelpColleaguePost.id == post_id).first()

    def get_all_posts(
        self,
        category: Optional[str] = None,
        status: str = "open",
        sort: str = "new",  # new, hot, top
        tags: Optional[List[str]] = None,
        limit: int = 20,
        page: int = 1
    ) -> List[HelpColleaguePost]:
        """Get all posts with optional filtering and sorting"""
        query = self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        )

        if status:
            query = query.filter(HelpColleaguePost.status == status)

        if category:
            query = query.filter(HelpColleaguePost.category == category)

        if tags:
            for tag_name in tags:
                query = query.filter(
                    HelpColleaguePost.tags.any(HelpColleagueTag.name == tag_name)
                )

        if sort == "hot":
            query = query.order_by(HelpColleaguePost.hot_score.desc())
        elif sort == "top":
            query = query.order_by(
                HelpColleaguePost.rating.desc(),
                HelpColleaguePost.responses_count.desc()
            )
        else:
            query = query.order_by(HelpColleaguePost.created_at.desc())

        offset = (page - 1) * limit
        return query.offset(offset).limit(limit).all()

    def get_user_posts(self, user_id: int, limit: int = 50) -> List[HelpColleaguePost]:
        """Get all posts by a specific user"""
        return self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        ).filter(
            HelpColleaguePost.user_id == user_id
        ).order_by(HelpColleaguePost.created_at.desc()).limit(limit).all()

    def get_post_count(self, user_id: int) -> int:
        return self.db.query(func.count(HelpColleaguePost.id)).filter(
            HelpColleaguePost.user_id == user_id
        ).scalar() or 0

    # ─── Responses ─────────────────────────────────────────────

    def create_response(
        self,
        post_id: int,
        user_id: int,
        content: str,
        rating: int = 0,
        is_from_bot: bool = False
    ) -> HelpColleagueResponse:
        """Create a response to a post"""
        response = HelpColleagueResponse(
            post_id=post_id,
            user_id=user_id,
            content=content,
            rating=rating,
            is_from_bot=is_from_bot
        )
        self.db.add(response)

        post = self.get_post_by_id(post_id)
        if post:
            post.responses_count = post.responses_count + 1
            self._recalc_hot_score(post)

            # Notify post author
            if post.user_id != user_id and not is_from_bot:
                self._create_notification(
                    user_id=post.user_id,
                    from_user_id=user_id,
                    post_id=post_id,
                    type="new_response",
                    message=f"Новый ответ на ваш пост «{post.title[:50]}»"
                )

        self.db.commit()
        self.db.refresh(response)
        return response

    def get_post_responses(self, post_id: int, limit: int = 50) -> List[HelpColleagueResponse]:
        """Get all responses to a post"""
        return self.db.query(HelpColleagueResponse).filter(
            HelpColleagueResponse.post_id == post_id
        ).order_by(
            desc(HelpColleagueResponse.is_from_bot),
            desc(HelpColleagueResponse.rating),
            HelpColleagueResponse.created_at.asc()
        ).limit(limit).all()

    def get_user_responses(self, user_id: int, limit: int = 50) -> List[HelpColleagueResponse]:
        return self.db.query(HelpColleagueResponse).filter(
            HelpColleagueResponse.user_id == user_id
        ).order_by(HelpColleagueResponse.created_at.desc()).limit(limit).all()

    def get_response_count(self, user_id: int) -> int:
        return self.db.query(func.count(HelpColleagueResponse.id)).filter(
            HelpColleagueResponse.user_id == user_id
        ).scalar() or 0

    # ─── Voting ────────────────────────────────────────────────

    def rate_response(self, response_id: int, user_id: int, rating: int) -> Optional[HelpColleagueResponse]:
        """Rate a response (-1, 0, or 1) with history"""
        if rating not in [-1, 0, 1]:
            raise ValueError("Rating must be -1, 0, or 1")

        response = self.db.query(HelpColleagueResponse).filter(
            HelpColleagueResponse.id == response_id
        ).first()

        if response:
            response.rating = rating
            self.db.commit()
            self.db.refresh(response)

            # Update post rating
            self.update_post_rating(response.post_id)
            self._recalc_hot_score(
                self.get_post_by_id(response.post_id)
            )

            # Notify response author about vote
            if rating != 0 and response.user_id != user_id and not response.is_from_bot:
                post = self.get_post_by_id(response.post_id)
                emoji = "👍" if rating > 0 else "👎"
                self._create_notification(
                    user_id=response.user_id,
                    from_user_id=user_id,
                    post_id=response.post_id,
                    type="response_rating",
                    message=f"{emoji} Оценка вашего ответа в «{(post.title if post else '')[:50]}»"
                )

        return response

    def vote_post(self, post_id: int, user_id: int, vote: int) -> Optional[HelpColleaguePost]:
        """Vote on a post directly (bypasses response-based rating)"""
        if vote not in [-1, 0, 1]:
            raise ValueError("Vote must be -1, 0, or 1")

        post = self.get_post_by_id(post_id)
        if not post:
            return None

        post.rating = (post.rating or 0) + vote
        self._recalc_hot_score(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update_post_rating(self, post_id: int) -> Optional[HelpColleaguePost]:
        """Update post rating based on responses"""
        post = self.get_post_by_id(post_id)
        if not post:
            return None

        avg_rating = self.db.query(
            func.avg(HelpColleagueResponse.rating)
        ).filter(
            HelpColleagueResponse.post_id == post_id
        ).scalar()

        if avg_rating is not None:
            post.rating = float(avg_rating)
            self.db.commit()
            self.db.refresh(post)

        return post

    # ─── Hot score ─────────────────────────────────────────────

    def _recalc_hot_score(self, post: Optional[HelpColleaguePost]):
        """Reddit-style hot score: upvotes / (age_hours + 2)^1.5"""
        if not post or not post.created_at:
            return
        created = post.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age_hours = max((now - created).total_seconds() / 3600, 0)
        score = max(post.rating, 0) + post.responses_count * 2
        post.hot_score = score / max((age_hours + 2) ** 1.5, 0.1)

    def recalc_all_hot_scores(self):
        posts = self.db.query(HelpColleaguePost).filter(
            HelpColleaguePost.status == "open"
        ).all()
        for p in posts:
            self._recalc_hot_score(p)
        self.db.commit()

    # ─── Close / Search ────────────────────────────────────────

    def close_post(self, post_id: int, user_id: int) -> Optional[HelpColleaguePost]:
        """Close a post (only owner can close)"""
        post = self.get_post_by_id(post_id)

        if post and post.user_id == user_id:
            post.status = "closed"
            self._recalc_hot_score(post)
            self.db.commit()
            self.db.refresh(post)

        return post

    def search_posts(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[HelpColleaguePost]:
        """Search posts by title and description"""
        search_pattern = f"%{query_text}%"

        return self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        ).filter(
            HelpColleaguePost.status == "open",
            (HelpColleaguePost.title.ilike(search_pattern) |
             HelpColleaguePost.description.ilike(search_pattern))
        ).order_by(
            HelpColleaguePost.created_at.desc()
        ).limit(limit).all()

    def get_posts_by_category(self, category: str, limit: int = 20) -> List[HelpColleaguePost]:
        """Get posts filtered by category"""
        return self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        ).filter(
            HelpColleaguePost.category == category,
            HelpColleaguePost.status == "open"
        ).order_by(
            HelpColleaguePost.created_at.desc()
        ).limit(limit).all()

    def get_top_posts(self, limit: int = 100) -> List[HelpColleaguePost]:
        """Get top rated posts"""
        return self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        ).filter(
            HelpColleaguePost.status == "open"
        ).order_by(
            HelpColleaguePost.rating.desc(),
            HelpColleaguePost.responses_count.desc()
        ).limit(limit).all()

    def get_hot_posts(self, limit: int = 100) -> List[HelpColleaguePost]:
        return self.db.query(HelpColleaguePost).options(
            joinedload(HelpColleaguePost.tags)
        ).filter(
            HelpColleaguePost.status == "open"
        ).order_by(
            HelpColleaguePost.hot_score.desc()
        ).limit(limit).all()

    # ─── User Profile / Karma ──────────────────────────────────

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.id == user_id).first()

        karma = self.db.query(func.coalesce(func.sum(HelpColleagueResponse.rating), 0)).filter(
            HelpColleagueResponse.user_id == user_id,
            HelpColleagueResponse.is_from_bot == False
        ).scalar() or 0

        posts_count = self.get_post_count(user_id)
        responses_count = self.get_response_count(user_id)

        return {
            "id": user.id if user else user_id,
            "full_name": user.full_name if user else f"User #{user_id}",
            "karma": karma,
            "posts_count": posts_count,
            "responses_count": responses_count,
            "created_at": (user.created_at.isoformat() if user else None),
        }

    # ─── AI Response ───────────────────────────────────────────

    async def generate_ai_response(self, post: HelpColleaguePost) -> str:
        """Generate AI-powered response using GigaChat"""
        prompt = f"""Дай совет по следующему посту:
Заголовок: {post.title}
Категория: {post.category}
Описание: {post.description}

Дай 2-3 конкретные рекомендации."""

        response = await llm_client.chat(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7
        )

        if "не настроен" in response.lower() or "error" in response.lower():
            return self._get_fallback_response(post)

        return response

    def _get_fallback_response(self, post: HelpColleaguePost) -> str:
        """Fallback response when LLM is not configured"""
        category_responses = {
            "idea": "Интересная идея! Рекомендую протестировать на малой аудитории. Используйте A/B тесты.",
            "problem": "Попробуйте разбить проблему на меньшие части. Помогает анализ данных и лучшие практики.",
            "feedback": "Спасибо за обратную связь! Важно собирать мнения от разных стейкхолдеров.",
            "collaboration": "Четко определите роли, ожидания и метрики успеха перед стартом."
        }

        base = category_responses.get(post.category, "Рекомендую детально проанализировать ситуацию.")

        if len(post.description) > 200:
            base += " Готов помочь с конкретными рекомендациями."

        return base

    # ─── Notifications ─────────────────────────────────────────

    def _create_notification(
        self,
        user_id: int,
        from_user_id: Optional[int],
        post_id: int,
        type: str,
        message: str
    ):
        notif = HelpColleagueNotification(
            user_id=user_id,
            from_user_id=from_user_id,
            post_id=post_id,
            type=type,
            message=message
        )
        self.db.add(notif)
        self.db.flush()
        return notif

    def get_notifications(self, user_id: int, limit: int = 50) -> List[HelpColleagueNotification]:
        return self.db.query(HelpColleagueNotification).filter(
            HelpColleagueNotification.user_id == user_id
        ).order_by(
            HelpColleagueNotification.created_at.desc()
        ).limit(limit).all()

    def get_unread_notification_count(self, user_id: int) -> int:
        return self.db.query(func.count(HelpColleagueNotification.id)).filter(
            HelpColleagueNotification.user_id == user_id,
            HelpColleagueNotification.is_read == False
        ).scalar() or 0

    def mark_notifications_read(self, user_id: int):
        self.db.query(HelpColleagueNotification).filter(
            HelpColleagueNotification.user_id == user_id,
            HelpColleagueNotification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
