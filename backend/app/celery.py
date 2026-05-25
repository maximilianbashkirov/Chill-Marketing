# Celery configuration for async tasks

from celery import Celery
from .config import settings

celery_app = Celery(
    'chillbot',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def analyze_marketing_idea_task(self, idea_description: str, user_id: int):
    """Celery task for analyzing marketing ideas"""
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    from .services.analytics import AnalyticsService
    
    db = SessionLocal()
    try:
        service = AnalyticsService(db)
        # This will be implemented when LLM is connected
        result = {
            "status": "completed",
            "message": "Task completed (mock)"
        }
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def analyze_content_task(self, content_type: str, idea_description: str, user_id: int):
    """Celery task for content analysis"""
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    from .services.content import ContentService
    
    db = SessionLocal()
    try:
        service = ContentService(db)
        result = {
            "status": "completed",
            "message": "Task completed (mock)"
        }
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def conduct_market_research_task(self, topic: str, user_id: int):
    """Celery task for market research"""
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    from .services.market_research import MarketResearchService
    
    db = SessionLocal()
    try:
        service = MarketResearchService(db)
        result = {
            "status": "completed",
            "message": "Task completed (mock)"
        }
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
