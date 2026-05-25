from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Marketing Case schemas
class MarketingCaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    result_metrics: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = None


class MarketingCaseCreate(MarketingCaseBase):
    pass


class MarketingCaseResponse(MarketingCaseBase):
    id: int
    vector_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Analytics schemas
class AnalyticsRequestCreate(BaseModel):
    idea: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    analysis_type: str = Field(default="idea", validation_alias="analysisType")
    
    @property
    def idea_description(self) -> str:
        return self.idea or ""


class AnalyticsRequestResponse(BaseModel):
    id: int
    user_id: int
    idea_description: str
    analysis_result: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content schemas
class ContentRequestCreate(BaseModel):
    content_type: Optional[str] = "post"
    content: Optional[str] = None
    idea: Optional[str] = None
    idea_description: Optional[str] = None
    target_audience: Optional[str] = None
    platform: Optional[str] = None
    
    @property
    def content_idea(self) -> str:
        return self.content or self.idea or self.idea_description or ""


class ContentRequestResponse(BaseModel):
    id: int
    user_id: int
    content_type: str
    idea_description: str
    target_audience: Optional[str] = None
    platform: Optional[str] = None
    success_prediction: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# SMI schemas
class SMIRequestCreate(BaseModel):
    topic: Optional[str] = None
    keywords: Optional[List[str]] = None


class SMIRequestResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    keywords: Optional[List[str]] = None
    articles_found: int
    relevance_score: Optional[float] = None
    viral_potential: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Market Research schemas
class MarketResearchRequestCreate(BaseModel):
    topic: Optional[str] = None
    industry: Optional[str] = None
    requirements: Optional[Dict[str, bool]] = None


class MarketResearchRequestResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    industry: Optional[str] = None
    research_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dot Analysis schemas
class DotAnalysisRequestCreate(BaseModel):
    case_description: Optional[str] = Field(None, alias="caseDescription")
    case_context: Optional[str] = None
    context: Optional[str] = None
    industry: Optional[str] = None
    
    @property
    def case_context_text(self) -> str:
        return self.case_description or self.case_context or self.context or ""
    
    class Config:
        populate_by_name = True


# Help Colleague schemas
class HelpColleaguePostCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: str = "idea"
    is_anonymous: bool = True


class DotAnalysisRequestResponse(BaseModel):
    id: int
    user_id: int
    case_context: str
    selected_models: Optional[List[Dict[str, Any]]] = None
    detailed_analysis: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Help Colleague schemas
class HelpColleaguePostCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: str = "idea"
    is_anonymous: bool = True
    tags: Optional[List[str]] = None


class HelpColleaguePostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    category: str  # idea, problem, feedback, collaboration
    is_anonymous: bool = True


class HelpColleaguePostCreateV2(HelpColleaguePostBase):
    tags: Optional[List[str]] = None


class HelpColleagueTagResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class HelpColleaguePostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category: str
    is_anonymous: bool
    responses_count: int
    rating: float
    hot_score: float
    status: str
    tags: List[HelpColleagueTagResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class HelpColleagueResponseBase(BaseModel):
    content: str = Field(..., min_length=10, max_length=3000)
    rating: int = 0  # -1 to 1


class HelpColleagueResponseCreate(HelpColleagueResponseBase):
    pass


class HelpColleagueResponseResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    rating: int
    is_from_bot: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class HelpColleagueProfileResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    karma: int = 0
    posts_count: int = 0
    responses_count: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HelpColleagueNotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    post_id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Common response schemas
class MessageResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
