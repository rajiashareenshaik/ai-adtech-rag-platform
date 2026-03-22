"""Campaign copilot agent.

This agent sits between FastAPI and the underlying services.
It is intentionally small: the real intelligence lives in the
retriever/vector store + the campaign service.
"""

from __future__ import annotations

from typing import Optional

from app.models.schemas import CampaignInsightRequest, CampaignInsightResponse
from app.services.campaign_service import CampaignService


class CampaignAgent:
    def __init__(self, service: CampaignService) -> None:
        self.service = service

    def answer(self, request: CampaignInsightRequest) -> CampaignInsightResponse:
        """Take a natural language question and return a grounded answer.

        In a real build, this would orchestrate LangGraph steps
        (retrieve -> reason -> recommend). For the scaffold, we keep
        the contract simple so everything else can evolve without
        breaking API callers.
        """

        audience = request.audience_segment or ""
        platform = request.platform or ""

        response = self.service.answer(
            question=request.question, audience_segment=audience, platform=platform
        )
        return response
