import pytest

import sql_tools as sql_tools_module
from judge import assert_criteria
from sql_agent import agent, ask
from utils import collect_tools


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    sql_tools_module.setup_database()


# ---------------------------------------------------------------------------
# Q3 — Basic result test
# ---------------------------------------------------------------------------

def test_trips_more_than_5_passengers():
    result = ask("How many trips had more than 5 passengers?")
    assert result.sql_query, "sql_query should be non-empty"
    # Expected answer: 22,413 — strip commas for flexible matching
    normalized = result.result_text.replace(",", "")
    assert "22413" in normalized, (
        f"Expected 22413 in result_text, got: {result.result_text}"
    )


# ---------------------------------------------------------------------------
# Q4 — Tool call order test
# ---------------------------------------------------------------------------

def test_tool_call_order():
    run_result = agent.run_sync("What is the most common payment type?")
    tools = collect_tools(run_result.all_messages())
    assert tools, "No tool calls recorded"
    assert tools[0] == "get_schema", f"First tool should be get_schema, got: {tools[0]}"
    assert "run_sql" in tools, "run_sql should be called at some point"


# ---------------------------------------------------------------------------
# Q5 — LLM judge test
# ---------------------------------------------------------------------------

def test_highest_fare_hour():
    result = ask("Which hour of the day has the highest average fare amount?")
    assert_criteria(
        result.sql_query,
        result.result_text,
        [
            "the SQL query correctly calculates average fare by hour of day",
            "the result identifies a specific hour as having the highest average fare",
            "the result includes the actual average fare amount",
        ],
    )


# ---------------------------------------------------------------------------
# Q6 — Additional tests
# ---------------------------------------------------------------------------

def test_avg_tip_credit_card():
    """tip_amount column should appear in query for credit card tip question."""
    result = ask("What is the average tip amount for credit card payments?")
    assert "tip_amount" in result.sql_query.lower(), (
        f"Expected 'tip_amount' in SQL query: {result.sql_query}"
    )
    assert result.result_text


def test_most_trips_pickup_location():
    """PULocationID column should appear in query."""
    result = ask("Which pickup location (PULocationID) has the most trips?")
    assert "pulocationid" in result.sql_query.lower(), (
        f"Expected 'pulocationid' in SQL query: {result.sql_query}"
    )
    assert result.result_text


def test_avg_fare_long_trips():
    """Both fare_amount and trip_distance should appear in query."""
    result = ask("What is the average fare for trips longer than 10 miles?")
    query_lower = result.sql_query.lower()
    assert "fare_amount" in query_lower, f"Expected 'fare_amount' in: {result.sql_query}"
    assert "trip_distance" in query_lower, f"Expected 'trip_distance' in: {result.sql_query}"
    assert result.result_text


def test_zero_passenger_trips():
    """passenger_count column should appear in filter."""
    result = ask("How many trips had zero passengers recorded?")
    assert "passenger_count" in result.sql_query.lower(), (
        f"Expected 'passenger_count' in SQL query: {result.sql_query}"
    )
    assert result.result_text


def test_busiest_day_of_week():
    """Tools should be called in order: get_schema then run_sql."""
    run_result = agent.run_sync("What is the busiest day of the week for taxi trips?")
    tools = collect_tools(run_result.all_messages())
    assert tools[0] == "get_schema"
    assert "run_sql" in tools
    assert run_result.output.result_text
