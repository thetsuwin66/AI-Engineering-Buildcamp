from pydantic import BaseModel
from pydantic_ai import Agent

import sql_tools as sql_tools_module


class SQLResult(BaseModel):
    sql_query: str
    result_text: str
    row_count: int


sql_tools = sql_tools_module.SQLTools()

agent = Agent(
    "openai:gpt-4o-mini",
    output_type=SQLResult,
    tools=[sql_tools.get_schema, sql_tools.run_sql],
    instructions=(
        "You are a SQL expert analyzing NYC taxi trip data. "
        "Always start by calling get_schema to understand the table structure "
        "before writing or running any SQL queries. "
        "Use run_sql to execute your queries. "
        "Return the exact SQL query used, the full result as text, and the row count of the result."
    ),
)


def ask(question: str) -> SQLResult:
    result = agent.run_sync(question)
    return result.output


if __name__ == "__main__":
    sql_tools_module.setup_database()
    question = "What's the average trip distance for rides with 2 passengers?"
    print(f"Question: {question}\n")
    result = ask(question)
    print(f"SQL:      {result.sql_query}")
    print(f"Result:   {result.result_text}")
    print(f"Rows:     {result.row_count}")
