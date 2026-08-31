"""MarketingCampaignFlow — Main Process Flow (5 steps)

Lifecycle:
  kickoff -> discovery_step (loop questioning) -> pause
  resume  -> after_discovery -> continue_discovery / "planning"
  ...     -> discovery_step -> pause -> ...
  resume  -> after_discovery -> "planning"
          -> planning_step (brand+channel) -> pause
  resume  -> after_planning -> "integration"
          -> integration_step -> pause
  resume  -> after_integration -> "content"
          -> content_step -> pause
  resume  -> after_content -> "finalize"
          -> finalize_step (Flow end)

Branch operations (redo_brand / rollback etc) are not handled inside Flow,
but intercepted by stream.py handler layer which calls Crew directly.
"""

from pydantic import BaseModel, ConfigDict

from crewai.flow import Flow, listen, or_, router, start
from crewai.flow.human_feedback import human_feedback

from .feedback_provider import PROVIDER
from .logger import make_logger
from .._crews.discovery_crew.discovery_crew import DiscoveryCrew
from .._crews.brand_creative_crew.brand_creative_crew import BrandCreativeCrew
from .._crews.channel_planning_crew.channel_planning_crew import ChannelPlanningCrew
from .._crews.integration_crew.integration_crew import IntegrationCrew
from .._crews.content_crew.content_crew import ContentCrew

log = make_logger("Flow")

MAX_DISCOVERY_ROUNDS = 4


class CampaignState(BaseModel):
    """Global state for Marketing Campaign Flow"""

    model_config = ConfigDict(extra="allow")

    # Basic info
    id: str = ""  # conversation_id, set via kickoff(inputs={"id": cid})
    campaign_name: str = ""
    campaign_brief: str = ""
    locale: str = "en"

    # Discovery phase
    qa_history: str = ""
    discovery_rounds: int = 0
    audience_profile: str = ""
    market_insights: str = ""

    # Planning phase
    brand_creatives: str = ""
    channel_plan: str = ""
    brand_confirmed: bool = False
    channel_confirmed: bool = False

    # Integration phase
    integrated_strategy: str = ""

    # Content phase
    copywriting: str = ""

    # Control
    current_phase: str = "discovery"
    finished: bool = False

    # Internal flags
    discovery_ready: bool = False  # [READY] detected — enough info for planning
    invalidated_phases: list = []  # phases that need regeneration due to upstream redo


class MarketingCampaignFlow(Flow[CampaignState]):
    """Marketing campaign main process — 5 steps + human_feedback pause/resume"""

    stream = True

    # ─── Discovery: Market analyst loop questioning ───────────────────────────

    @start()
    def begin(self):
        """Flow entry — initialization phase"""
        self.state.current_phase = "discovery"

    @listen(or_(begin, "continue_discovery"))
    @human_feedback(message="(user replies)", provider=PROVIDER)
    def discovery_step(self):
        """Market analyst asks a question or outputs [READY]"""
        s = self.state
        s.discovery_rounds += 1
        locale_instruction = "English"

        output = DiscoveryCrew().crew().kickoff(inputs={
            "campaign_brief": s.campaign_brief,
            "qa_history": s.qa_history or "(No previous Q&A)",
            "discovery_rounds": str(s.discovery_rounds),
            "locale_instruction": locale_instruction,
        })
        text = _crew_text(output)

        # Check if info is sufficient
        if "[READY]" in text:
            s.discovery_ready = True
            # [READY] can appear before or after the content — take the non-empty part
            parts = text.split("[READY]", 1)
            before = parts[0].strip()
            after = parts[1].strip() if len(parts) > 1 else ""
            # Use whichever side has the actual content
            content = after if len(after) > len(before) else before
            # Strip any [SUGGESTIONS] section from content
            if "[SUGGESTIONS]" in content:
                content = content.split("[SUGGESTIONS]")[0].strip()
            s.audience_profile = content
            s.market_insights = content
        else:
            # Append to qa_history
            clean = text.split("[SUGGESTIONS]")[0].strip() if "[SUGGESTIONS]" in text else text
            s.qa_history = (s.qa_history + f"\nAnalyst: {clean}").strip()

        return text

    @router(discovery_step)
    def after_discovery(self):
        # Check if user explicitly wants to skip discovery (e.g., "Enough info, start planning")
        feedback = ""
        if self.last_human_feedback:
            feedback = (self.last_human_feedback.feedback or "").lower()
        if self.state.discovery_ready or self.state.discovery_rounds >= MAX_DISCOVERY_ROUNDS:
            # Ensure audience_profile is set (fallback to qa_history if [READY] didn't fire)
            if not self.state.audience_profile:
                self.state.audience_profile = self.state.qa_history
                self.state.market_insights = self.state.qa_history
            return "planning"
        if any(k in feedback for k in ("skip", "confirm", "action:confirm", "next")):
            # User wants to skip — use whatever info we have
            if not self.state.audience_profile:
                self.state.audience_profile = self.state.qa_history
                self.state.market_insights = self.state.qa_history
            return "planning"
        return "continue_discovery"

    # ─── Planning: Brand creative + Channel planning (sequential, streaming output) ─────

    @listen("planning")
    @human_feedback(message="(user reviews)", provider=PROVIDER)
    def planning_step(self):
        """Brand creative -> Channel planning (sequential, streaming auto-segmented)"""
        s = self.state
        s.current_phase = "planning"
        locale_instruction = "English"

        inputs = {
            "campaign_name": s.campaign_name,
            "campaign_brief": s.campaign_brief,
            "audience_profile": s.audience_profile,
            "market_insights": s.market_insights,
            "locale_instruction": locale_instruction,
        }

        brand_result = BrandCreativeCrew().crew().kickoff(inputs=inputs)
        s.brand_creatives = _crew_text(brand_result)

        channel_result = ChannelPlanningCrew().crew().kickoff(inputs=inputs)
        s.channel_plan = _crew_text(channel_result)

        return f"{s.brand_creatives}\n\n---\n\n{s.channel_plan}"

    @router(planning_step)
    def after_planning(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if _is_confirm(feedback):
            return "integration"
        if "redo_brand" in feedback:
            return "redo_brand"
        if "redo_channel" in feedback:
            return "redo_channel"
        return "planning"

    # ─── Redo Brand / Channel (streaming, stays in planning phase) ────────

    @listen("redo_brand")
    @human_feedback(message="(user reviews)", provider=PROVIDER)
    def redo_brand_step(self):
        """Redo Brand Creative"""
        s = self.state
        locale_instruction = "English"
        feedback_text = ""
        if self.last_human_feedback:
            raw = self.last_human_feedback.feedback or ""
            if "|feedback=" in raw:
                feedback_text = raw.split("|feedback=", 1)[1]

        result = BrandCreativeCrew().crew().kickoff(inputs={
            "campaign_name": s.campaign_name,
            "campaign_brief": s.campaign_brief + (f"\n\nFeedback: {feedback_text}" if feedback_text else ""),
            "audience_profile": s.audience_profile,
            "market_insights": s.market_insights,
            "locale_instruction": locale_instruction,
        })
        s.brand_creatives = _crew_text(result)
        s.current_phase = "planning"
        # Mark downstream phases as needing regeneration
        s.invalidated_phases = list(set(s.invalidated_phases + ["integration", "content", "finalize"]))
        return s.brand_creatives

    @router(redo_brand_step)
    def after_redo_brand(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if _is_confirm(feedback):
            return "integration"
        if "redo_brand" in feedback:
            return "redo_brand"
        if "redo_channel" in feedback:
            return "redo_channel"
        return "planning"

    @listen("redo_channel")
    @human_feedback(message="(user reviews)", provider=PROVIDER)
    def redo_channel_step(self):
        """Redo Channel Strategy"""
        s = self.state
        locale_instruction = "English"
        feedback_text = ""
        if self.last_human_feedback:
            raw = self.last_human_feedback.feedback or ""
            if "|feedback=" in raw:
                feedback_text = raw.split("|feedback=", 1)[1]

        result = ChannelPlanningCrew().crew().kickoff(inputs={
            "campaign_name": s.campaign_name,
            "campaign_brief": s.campaign_brief + (f"\n\nFeedback: {feedback_text}" if feedback_text else ""),
            "audience_profile": s.audience_profile,
            "market_insights": s.market_insights,
            "locale_instruction": locale_instruction,
        })
        s.channel_plan = _crew_text(result)
        s.current_phase = "planning"
        # Mark downstream phases as needing regeneration
        s.invalidated_phases = list(set(s.invalidated_phases + ["integration", "content", "finalize"]))
        return s.channel_plan

    @router(redo_channel_step)
    def after_redo_channel(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if _is_confirm(feedback):
            return "integration"
        if "redo_brand" in feedback:
            return "redo_brand"
        if "redo_channel" in feedback:
            return "redo_channel"
        return "planning"

    # ─── Integration: Strategy integration ───────────────────────────────────

    @listen("integration")
    @human_feedback(message="(user reviews)", provider=PROVIDER)
    def integration_step(self):
        """Strategy director integrates brand+channel into unified plan"""
        s = self.state
        s.current_phase = "integration"
        locale_instruction = "English"

        result = IntegrationCrew().crew().kickoff(inputs={
            "campaign_name": s.campaign_name,
            "audience_profile": s.audience_profile,
            "selected_creative": s.brand_creatives,
            "channel_plan": s.channel_plan,
            "locale_instruction": locale_instruction,
        })
        s.integrated_strategy = _crew_text(result)
        # Clear this phase from invalidated list (it was just regenerated)
        s.invalidated_phases = [p for p in s.invalidated_phases if p != "integration"]
        return s.integrated_strategy

    @router(integration_step)
    def after_integration(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if _is_confirm(feedback):
            return "content"
        return "integration"

    # ─── Content: Copy production ───────────────────────────────────────

    @listen("content")
    @human_feedback(message="(user reviews)", provider=PROVIDER)
    def content_step(self):
        """Copywriter produces marketing copy"""
        s = self.state
        s.current_phase = "content"
        locale_instruction = "English"

        result = ContentCrew().crew().kickoff(inputs={
            "campaign_name": s.campaign_name,
            "integrated_strategy": s.integrated_strategy,
            "selected_creative": s.brand_creatives,
            "locale_instruction": locale_instruction,
        })
        s.copywriting = _crew_text(result)
        # Clear this phase from invalidated list (it was just regenerated)
        s.invalidated_phases = [p for p in s.invalidated_phases if p != "content"]
        return s.copywriting

    @router(content_step)
    def after_content(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if _is_confirm(feedback):
            return "finalize"
        return "content"

    # ─── Finalize ────────────────────────────────────────────────

    @listen("finalize")
    @human_feedback(message="(user reviews final plan)", provider=PROVIDER)
    def finalize_step(self):
        """Finalization phase - Flow pauses awaiting user to generate full plan or finish"""
        self.state.current_phase = "finalize"
        return "All modules complete. Ready to generate full plan."

    @router(finalize_step)
    def after_finalize(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if _is_confirm(feedback) or "generate" in feedback.lower():
            return "generate_document"
        if "revise" in feedback.lower() or "iteration_feedback" in feedback:
            return "revise_document"
        return "finalize"

    @listen("generate_document")
    @human_feedback(message="(user reviews document)", provider=PROVIDER)
    def generate_document_step(self):
        """Generate full plan document"""
        s = self.state
        locale_instruction = "English"

        # Build comprehensive input for full document generation
        full_brief = f"""You are generating a COMPLETE marketing campaign plan document.
Below is ALL the material produced by the team. Your job is to compile it into
ONE structured, professional marketing plan document with the following chapters:

1. Executive Summary
2. Target Audience Analysis
3. Brand & Creative Strategy
4. Channel & Media Plan
5. Integrated Campaign Strategy
6. Content & Copywriting
7. Timeline & Milestones
8. Budget Allocation
9. KPIs & Success Metrics

Use the material below as source. Expand where needed, add timeline and budget
estimates based on the channel plan, and ensure the document reads as a cohesive
professional marketing plan that a team can execute from.

─── SOURCE MATERIAL ───

Campaign Name: {s.campaign_name}

── Audience Profile ──
{s.audience_profile}

── Brand & Creative ──
{s.brand_creatives}

── Channel Strategy ──
{s.channel_plan}

── Integrated Strategy ──
{s.integrated_strategy}

── Marketing Copy ──
{s.copywriting}
"""

        result = IntegrationCrew().crew().kickoff(inputs={
            "campaign_name": s.campaign_name,
            "audience_profile": full_brief,
            "selected_creative": "",
            "channel_plan": "",
            "locale_instruction": locale_instruction,
        })
        s.integrated_strategy = _crew_text(result)
        return s.integrated_strategy

    @router(generate_document_step)
    def after_generate_document(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if "revise" in feedback.lower() or "|feedback=" in feedback:
            return "revise_document"
        if _is_confirm(feedback):
            return "done"
        return "generate_document"

    @listen("revise_document")
    @human_feedback(message="(user reviews revised document)", provider=PROVIDER)
    def revise_document_step(self):
        """Revise plan document"""
        s = self.state
        locale_instruction = "English"

        # Extract feedback from the human feedback
        revision_feedback = ""
        if self.last_human_feedback:
            raw = self.last_human_feedback.feedback or ""
            if "|feedback=" in raw:
                revision_feedback = raw.split("|feedback=", 1)[1]
            else:
                revision_feedback = raw

        result = IntegrationCrew().crew().kickoff(inputs={
            "campaign_name": s.campaign_name,
            "audience_profile": s.integrated_strategy,
            "selected_creative": "",
            "channel_plan": "",
            "locale_instruction": locale_instruction + f'\n\nRevise the document based on this feedback: "{revision_feedback}"',
        })
        s.integrated_strategy = _crew_text(result)
        return s.integrated_strategy

    @router(revise_document_step)
    def after_revise_document(self):
        feedback = (self.last_human_feedback.feedback or "") if self.last_human_feedback else ""
        if "revise" in feedback.lower() or "|feedback=" in feedback:
            return "revise_document"
        if _is_confirm(feedback):
            return "done"
        return "generate_document"

    @listen("done")
    def done_step(self):
        """Flow end"""
        self.state.finished = True
        return "Done."


# ─── Helpers ─────────────────────────────────────────────────────

def _crew_text(output) -> str:
    """Extract text from CrewOutput."""
    raw = getattr(output, "raw", None)
    return str(raw).strip() if raw else str(output).strip()


def _is_confirm(feedback: str) -> bool:
    """Check if feedback indicates confirmation."""
    lower = feedback.lower().strip()
    return any(k in lower for k in (
        "confirm", "action:confirm",
        "approve", "next", "finalize",
    ))
