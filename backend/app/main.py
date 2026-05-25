from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .config import settings
from .api import (
    analytics_router,
    content_router,
    smi_router,
    market_research_router,
    dot_analysis_router,
    help_colleague_router,
    trends_router
)
from .utils.vector_store import vector_db


def create_tables():
    """Create database tables + run migrations"""
    Base.metadata.create_all(bind=engine)
    # Migration: add hot_score to existing help_colleague_posts table
    try:
        from sqlalchemy import inspect, text
        with engine.connect() as conn:
            if engine.dialect.has_table(conn, "help_colleague_posts"):
                inspector = inspect(engine)
                columns = [c["name"] for c in inspector.get_columns("help_colleague_posts")]
                if "hot_score" not in columns:
                    conn.execute(text("ALTER TABLE help_colleague_posts ADD COLUMN hot_score FLOAT DEFAULT 0.0"))
                    conn.commit()
                    print("Migration: added hot_score column")
    except Exception as e:
        print(f"Migration note: {e}")
    print("Database tables created successfully")


def initialize_vector_db():
    """Initialize Qdrant vector database"""
    try:
        vector_db.initialize_collection()
        print("Vector database initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize vector database: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Chill Marketing AI Bot - Интеллектуальная система поддержки принятия решений в маркетинге",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(analytics_router, prefix="/api/v1")
    app.include_router(content_router, prefix="/api/v1")
    app.include_router(smi_router, prefix="/api/v1")
    app.include_router(market_research_router, prefix="/api/v1")
    app.include_router(dot_analysis_router, prefix="/api/v1")
    app.include_router(help_colleague_router, prefix="/api/v1")
    app.include_router(trends_router, prefix="/api/v1")
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        create_tables()
        initialize_vector_db()
        print(f"{settings.APP_NAME} v{settings.APP_VERSION} started successfully!")
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "Интеллектуальная система поддержки принятия решений в маркетинге",
            "docs": "/docs",
            "modules": [
                "Analytics - Аналитика маркетинговых идей",
                "Content - Анализатор идей для контента",
                "SMI - Проверка актуальности тем",
                "Market Research - Исследования рынка",
                "Dot Analysis - Подбор маркетинговых моделей",
                "Help Colleague - Сообщество для обмена идеями"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    return app


app = create_app()
