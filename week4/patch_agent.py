from pydantic_ai import Agent

# GPT-4o-mini pricing per token (as of 2024)
INPUT_COST_PER_TOKEN = 0.15 / 1_000_000
OUTPUT_COST_PER_TOKEN = 0.60 / 1_000_000

_state = {"total_cost": 0.0, "patched": False}
_original_run_sync = None


def patch_agent():
    """Monkey-patch Agent.run_sync to accumulate token costs."""
    global _original_run_sync

    if _state["patched"]:
        return

    _original_run_sync = Agent.run_sync

    def _tracked_run_sync(self, *args, **kwargs):
        result = _original_run_sync(self, *args, **kwargs)
        u = result.usage()
        cost = u.input_tokens * INPUT_COST_PER_TOKEN + u.output_tokens * OUTPUT_COST_PER_TOKEN
        _state["total_cost"] += cost
        return result

    Agent.run_sync = _tracked_run_sync
    _state["patched"] = True


def get_total_cost() -> float:
    return _state["total_cost"]


def reset_cost():
    _state["total_cost"] = 0.0
