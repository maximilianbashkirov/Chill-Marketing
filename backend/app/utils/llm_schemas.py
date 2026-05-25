from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AnalyticsResponse(BaseModel):
    success_probability: float = Field(default=0.5, ge=0, le=1)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    similar_cases: List[Any] = Field(default_factory=list)
    suggested_models: List[str] = Field(default_factory=list)
    ai_summary: str = ""
    propagation_suggestions: List[str] = Field(default_factory=list)


class CompetitorAnalysisResponse(BaseModel):
    company_info: Dict[str, Any] = Field(default_factory=dict)
    business_metrics: Dict[str, Any] = Field(default_factory=dict)
    market_position: Dict[str, Any] = Field(default_factory=list)
    products_services: List[Dict[str, Any]] = Field(default_factory=list)
    pricing: Dict[str, Any] = Field(default_factory=dict)
    marketing_channels: List[str] = Field(default_factory=list)
    online_presence: Dict[str, Any] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)


class SWOTAnalysisResponse(BaseModel):
    business_description: str = ""
    strengths: List[Dict[str, Any]] = Field(default_factory=list)
    weaknesses: List[Dict[str, Any]] = Field(default_factory=list)
    opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    strategies: Dict[str, List[str]] = Field(default_factory=dict)
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    pest_factors: Dict[str, List[str]] = Field(default_factory=dict)
    kpis: List[Dict[str, Any]] = Field(default_factory=list)
    competitor_comparison: List[Dict[str, Any]] = Field(default_factory=list)


class AudienceAnalysisResponse(BaseModel):
    product_description: str = ""
    total_addressable_market: str = ""
    segments: List[Dict[str, Any]] = Field(default_factory=list)
    primary_persona: Dict[str, Any] = Field(default_factory=dict)
    behavioral_traits: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    motivations: List[str] = Field(default_factory=list)
    preferred_channels: List[str] = Field(default_factory=list)
    decision_factors: List[str] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ContentAnalysisResponse(BaseModel):
    success_probability: float = Field(default=0.5, ge=0, le=1)
    viral_potential: float = Field(default=0.5, ge=0, le=1)
    engagement_prediction: Dict[str, str] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    best_posting_time: str = "19:00-21:00"
    suggested_hashtags: List[str] = Field(default_factory=list)
    originality_score: float = Field(default=0.5, ge=0, le=1)
    similar_content: List[Dict[str, Any]] = Field(default_factory=list)
    trend_alignment: Dict[str, Any] = Field(default_factory=dict)
    format_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    content_ideas: List[str] = Field(default_factory=list)
    key_words: List[str] = Field(default_factory=list)
    posting_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    target_audience: str = ""
    audience_segments: List[Dict[str, Any]] = Field(default_factory=list)


class SMIResponse(BaseModel):
    articles_found: int = 0
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    viral_potential: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    best_platforms: List[str] = Field(default_factory=list)
    estimated_reach: str = ""


class MarketResearchResponse(BaseModel):
    statistics: Dict[str, Any] = Field(default_factory=dict)
    cases: List[Dict[str, Any]] = Field(default_factory=list)
    strategies: List[Dict[str, Any]] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    trends: List[str] = Field(default_factory=list)
    benchmarks: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)


class DotAnalysisResponse(BaseModel):
    selected_models: List[Dict[str, Any]] = Field(default_factory=list)
    detailed_analysis: Dict[str, Any] = Field(default_factory=dict)


class HelpColleagueResponse(BaseModel):
    advice: List[str] = Field(default_factory=list)
    summary: str = ""