from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analytics_requests = relationship("AnalyticsRequest", back_populates="user")
    content_requests = relationship("ContentRequest", back_populates="user")
    smi_requests = relationship("SMIRequest", back_populates="user")
    market_research_requests = relationship("MarketResearchRequest", back_populates="user")
    dot_analysis_requests = relationship("DotAnalysisRequest", back_populates="user")
    help_colleague_posts = relationship("HelpColleaguePost", back_populates="user")
    help_colleague_responses = relationship("HelpColleagueResponse", back_populates="user")


class MarketingCase(Base):
    __tablename__ = "marketing_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # analytics, content, smi, etc.
    industry = Column(String)
    company_size = Column(String)  # startup, smb, enterprise
    result_metrics = Column(JSON)  # {roi: 150%, conversion: 3.2%, etc.}
    source_url = Column(String)
    vector_id = Column(String, index=True)  # Qdrant vector ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalyticsRequest(Base):
    __tablename__ = "analytics_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    idea_description = Column(Text, nullable=False)
    analysis_result = Column(JSON)  # {success_probability, recommendations, similar_cases}
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="analytics_requests")


class ContentRequest(Base):
    __tablename__ = "content_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_type = Column(String)  # post, reel, podcast, article
    idea_description = Column(Text, nullable=False)
    target_audience = Column(String)
    platform = Column(String)  # instagram, telegram, youtube, etc.
    success_prediction = Column(JSON)  # {probability, viral_potential, recommendations}
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="content_requests")


class SMIRequest(Base):
    __tablename__ = "smi_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, nullable=False)
    keywords = Column(JSON)  # list of keywords
    articles_found = Column(Integer, default=0)
    relevance_score = Column(Float)  # 0-1 score
    viral_potential = Column(JSON)  # {score, similar_articles, trends}
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="smi_requests")


class SMIArticle(Base):
    __tablename__ = "smi_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, nullable=False)
    source_url = Column(String)
    title = Column(Text, nullable=False)
    description = Column(Text)
    full_text = Column(Text)
    link = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True))
    category = Column(String)
    content_hash = Column(String, index=True)
    topic = Column(String, index=True)
    relevance_score = Column(Float, default=0.5)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))


class SMICache(Base):
    __tablename__ = "smi_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False, index=True)
    search_query = Column(String)
    articles_found = Column(Integer, default=0)
    cached_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))


class MarketResearchRequest(Base):
    __tablename__ = "market_research_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, nullable=False)
    industry = Column(String)
    research_data = Column(JSON)  # {statistics, cases, strategies, examples}
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="market_research_requests")


class DotAnalysisRequest(Base):
    __tablename__ = "dot_analysis_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    case_context = Column(Text, nullable=False)
    selected_models = Column(JSON)  # [{model_name, description, applicability_score}]
    detailed_analysis = Column(JSON)  # Full analysis with each model
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="dot_analysis_requests")


class HelpColleagueTag(Base):
    __tablename__ = "help_colleague_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HelpColleaguePostTag(Base):
    __tablename__ = "help_colleague_post_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("help_colleague_posts.id", ondelete="CASCADE"))
    tag_id = Column(Integer, ForeignKey("help_colleague_tags.id", ondelete="CASCADE"))


class HelpColleagueNotification(Base):
    __tablename__ = "help_colleague_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("help_colleague_posts.id", ondelete="CASCADE"))
    type = Column(String)  # new_response, response_rating, post_closed, ai_ready
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    from_user = relationship("User", foreign_keys=[from_user_id])


class HelpColleaguePost(Base):
    __tablename__ = "help_colleague_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)  # idea, problem, feedback, collaboration
    is_anonymous = Column(Boolean, default=True)
    responses_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    hot_score = Column(Float, default=0.0)
    status = Column(String, default="open")  # open, closed, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="help_colleague_posts")
    responses = relationship("HelpColleagueResponse", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("HelpColleagueTag", secondary="help_colleague_post_tags", lazy="selectin")


class HelpColleagueResponse(Base):
    __tablename__ = "help_colleague_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("help_colleague_posts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    rating = Column(Integer, default=0)  # -1 to 1 (dislike, neutral, like)
    is_from_bot = Column(Boolean, default=False)  # If response generated by AI
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    post = relationship("HelpColleaguePost", back_populates="responses")
    user = relationship("User", back_populates="help_colleague_responses")


class HelpColleagueRatingHistory(Base):
    __tablename__ = "help_colleague_rating_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_type = Column(String)  # "post" or "response"
    target_id = Column(Integer)
    vote = Column(Integer)  # -1 or 1
    created_at = Column(DateTime(timezone=True), server_default=func.now())
