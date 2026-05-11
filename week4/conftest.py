import pytest
from patch_agent import get_total_cost, patch_agent, reset_cost

patch_agent()


@pytest.fixture(scope="session", autouse=True)
def cost_tracker():
    reset_cost()
    yield
    total = get_total_cost()
    print(f"\n{'='*40}")
    print(f"Total estimated API cost: ${total:.4f}")
    print(f"{'='*40}")
