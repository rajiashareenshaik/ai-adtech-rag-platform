from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.schemas import (
    CampaignInsightRequest,
    CampaignInsightResponse,
    Insight,
    RecommendedAction,
)


@dataclass(frozen=True)
class CampaignRecord:
    id: str
    name: str
    platform: str
    objective: str
    stats: Dict[str, Any]
    creatives: List[str]
    audience_segment: str


class CampaignService:
    """Thin business layer around campaign data.

    This is where you can add more realistic rules for prioritization, scoring, etc.
    """

    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self._campaigns = self._load()

    def _load(self) -> Dict[str, CampaignRecord]:
        data = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        campaigns: Dict[str, CampaignRecord] = {}
        for row in data:
            campaigns[row["id"]] = CampaignRecord(
                id=row["id"],
                name=row["name"],
                platform=row["platform"],
                objective=row.get("objective", ""),
                stats=row.get("stats", {}),
                creatives=row.get("creatives", []),
                audience_segment=row.get("audience_segment", "unknown"),
            )
        return campaigns

    def get_campaign(self, campaign_id: str) -> Optional[CampaignRecord]:
        return self._campaigns.get(campaign_id)

    def list_campaigns(self) -> List[CampaignRecord]:
        return list(self._campaigns.values())

    def build_context(self, request: CampaignInsightRequest) -> str:
        """Build a compact context string for retrieval/LLM."""

        bundle: List[CampaignRecord]
        if request.campaign_id and (c := self.get_campaign(request.campaign_id)):
            bundle = [c]
        else:
            bundle = self.list_campaigns()[:5]

        lines = ["campaigns="]
        for c in bundle:
            lines.append(
                f"- {c.id} | {c.name} | platform={c.platform} | audience={c.audience_segment} | "
                f"objective={c.objective} | stats={c.stats}"
            )

        if request.time_range:
            lines.append(f"time_range_hint={request.time_range}")

        if request.audience_segment:
            lines.append(f"audience_segment_filter={request.audience_segment}")

        return "\n".join(lines)

    def summarize_actions(self, request: CampaignInsightRequest) -> List[RecommendedAction]:
        # This is intentionally light—it's meant to be overridden by real rules later.
        actions: List[RecommendedAction] = []
        if request.include_recommendations:
            actions.append(
                RecommendedAction(
                    summary="Test fresh creatives for fatigue",
                    rationale="If CTR is sliding, new creative often beats tweaks",
                    priority="high",
                )
            )
            actions.append(
                RecommendedAction(
                    summary="Shift budget toward winners",
                    rationale="Reallocate spend to the best ROAS segment before you do big changes",
                    priority="medium",
                )
            )
        return actions

    def answer(self, request: CampaignInsightRequest) -> CampaignInsightResponse:
        """Placeholder business response.

        The LangGraph + RAG agent should call this with richer context, but in a pinch
        this gives us a deterministic answer.
        """

        ctx = self.build_context(request)
        return CampaignInsightResponse(
            question=request.question,
            answer="This is where the LangGraph + RAG answer will show up.",
            reasoning=["Loaded campaign context", "Ready for retrieval and generation"],
            insights=[Insight(title="Context", details=ctx)],
            actions=self.summarize_actions(request),
        )


@lru_cache(maxsize=1)
def get_campaign_service() -> CampaignService:
    # app/services -> app -> repo root
    repo_root = Path(__file__).resolve().parents[2]
    dataset_path = repo_root / "data" / "campaigns.json"
    return CampaignService(dataset_path)
