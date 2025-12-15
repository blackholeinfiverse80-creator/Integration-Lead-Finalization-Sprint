from typing import Dict, Any, List
from src.utils.noopur_client import NoopurClient
from config.config import INTEGRATOR_USE_NOOPUR


class CreatorRouter:
    """Routing helpers for CreatorCore flows (pre-prompt warming, feedback forwarding)."""

    def __init__(self, memory_adapter=None):
        self.memory = memory_adapter
        self.noopur = NoopurClient() if INTEGRATOR_USE_NOOPUR else None

    def prewarm_and_prepare(self, request: str, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch related context (top-3) and attach to input_data under `related_context`."""
        # If noopur integration enabled, prefer calling Noopur's generate with topic/goal
        try:
            topic = input_data.get("topic") or input_data.get("data", {}).get("topic")
            goal = input_data.get("goal") or input_data.get("data", {}).get("goal")
            gen_type = input_data.get("type") or input_data.get("data", {}).get("type", "story")

            if self.noopur and topic and goal:
                payload = {"topic": topic, "goal": goal, "type": gen_type}
                resp = self.noopur.generate(payload)
                related = resp.get("related_context") or resp.get("related_context", [])
                input_data.setdefault("related_context", related)
                return input_data

            # Fallback: use local memory adapter to fetch context (if memory stores topic indexed data)
            if self.memory and user_id:
                ctx = self.memory.get_context(user_id, limit=3)
                input_data.setdefault("related_context", ctx)

        except Exception:
            # swallow integration errors and return original data to avoid breaking API
            return input_data

        return input_data

    def forward_feedback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize and forward to Noopur feedback endpoint
        if not self.noopur:
            return {"status": "disabled"}
        # Try multiple payload shapes
        body = {}
        if "id" in payload and "feedback" in payload:
            body = {"id": payload["id"], "feedback": payload["feedback"]}
        elif "generation_id" in payload and "command" in payload:
            body = {"generation_id": payload["generation_id"], "command": payload["command"]}
        else:
            body = payload

        return self.noopur.feedback(body)
