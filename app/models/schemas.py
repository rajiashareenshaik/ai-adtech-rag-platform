from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CampaignInsightRequest(BaseModel):
    """Input schema for asking the platform a question."""

    question: str = Field(..., description="Natural language question like 'Why did CTR drop last week?'" )
    campaign_id: Optional[str] = Field(None, description="Optional campaign identifier")
    time_range: Optional[str] = Field(None, description="Optional time range hint, e.g. 'last 7 days'")
    audience_segment: Optional[str] = Field(None, description="Optional audience filter")
    include_recommendations: bool = Field(True, description="Toggle recommendations in response")


class Insight(BaseModel):
    title: str
    details: str


class RecommendedAction(BaseModel):
    summary: str
    rationale: str
    priority: str = Field(
        default="medium",
        description="low/medium/high (this is a hint, not a strict rule)",
    )


class CampaignInsightResponse(BaseModel):
    """LLM + RAG response payload."""

    question: str
    answer: str
    reasoning: List[str] = []
    insights: List[Insight] = []
    actions: List[RecommendedAction] = []
