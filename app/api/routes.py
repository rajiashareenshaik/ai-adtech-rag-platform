from fastapi import APIRouter, Depends

from app.models.schemas import (
    CampaignInsightRequest,
    CampaignInsightResponse,
)
from app.services.campaign_service import get_campaign_service
from app.agents.campaign_agent import CampaignAgent

router = APIRouter(tags=["campaign"])


@router.get("/ping")
async def ping() -> dict:
    return {"ping": "pong"}


@router.post("/insights", response_model=CampaignInsightResponse)
async def insights(
    payload: CampaignInsightRequest,
    service=Depends(get_campaign_service),
) -> CampaignInsightResponse:
    agent = CampaignAgent(service=service)

    # This endpoint is the “business logic shortcut” for marketing users.
    # They ask in natural language; we hand it off to the agent pipeline.
    return await agent.answer(payload)
