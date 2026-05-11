from pydantic import BaseModel
from pydantic_ai import Agent


class JudgeResult(BaseModel):
    passed: bool
    reason: str


_judge = Agent(
    "openai:gpt-4o-mini",
    output_type=JudgeResult,
    instructions=(
        "You are an evaluator. Assess whether the given agent output meets ALL specified criteria. "
        "Return passed=True only if every criterion is fully satisfied."
    ),
)


def evaluate_agent_performance(sql_query: str, result_text: str, criteria: list[str]) -> JudgeResult:
    """Use an LLM judge to evaluate agent output against a list of criteria."""
    criteria_text = "\n".join(f"- {c}" for c in criteria)
    prompt = f"""Evaluate this agent output against the criteria below.

IMPORTANT: Judge only what is directly observable in the SQL query and result text provided.
Do NOT require external data validation or question whether the numbers are correct —
assume the database returned accurate results. Evaluate structural and logical correctness only.

SQL Query:
{sql_query}

Result:
{result_text}

Criteria:
{criteria_text}

Respond with passed=True if all criteria are structurally and logically met based on what you can observe."""
    result = _judge.run_sync(prompt)
    return result.output


def assert_criteria(sql_query: str, result_text: str, criteria: list[str]) -> None:
    """Assert all criteria pass via LLM judge; raises AssertionError on failure."""
    judgment = evaluate_agent_performance(sql_query, result_text, criteria)
    assert judgment.passed, f"LLM judge failed: {judgment.reason}"
