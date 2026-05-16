"""Script for Questions 5 & 6: query Logfire traces and calculate costs."""
from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
from logfire.query_client import AsyncLogfireQueryClient

READ_TOKEN = os.environ.get("LOGFIRE_READ_TOKEN", "your-read-token-here")

MODEL_PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    prices = MODEL_PRICES[model_name.lower()]
    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]
    return input_cost + output_cost


async def get_session_traces():
    async with AsyncLogfireQueryClient(read_token=READ_TOKEN) as client:
        # Q5: Get all top-level trivia_session spans with their trace IDs
        sql = """
            SELECT
                trace_id,
                span_id,
                start_timestamp,
                end_timestamp,
                span_name
            FROM records
            WHERE span_name = 'trivia_session'
            ORDER BY start_timestamp DESC
            LIMIT 10
        """
        result = await client.query_json_rows(sql)
        sessions = result['rows']

        print("=== Trivia Session Traces (Q5) ===")
        for s in sessions:
            print(f"trace_id: {s['trace_id']}  started: {s['start_timestamp']}")

        if not sessions:
            print("No sessions found. Run the agent first.")
            return

        # Use the most recent session for cost analysis
        target_trace = sessions[0]['trace_id']
        print(f"\nAnalyzing trace: {target_trace}")

        # Q6: Get token usage for the session
        sql_tokens = f"""
            SELECT
                SUM(CAST(attributes->>'gen_ai.usage.input_tokens' AS BIGINT)) AS total_input,
                SUM(CAST(attributes->>'gen_ai.usage.output_tokens' AS BIGINT)) AS total_output
            FROM records
            WHERE trace_id = '{target_trace}'
              AND attributes->>'gen_ai.usage.input_tokens' IS NOT NULL
        """
        result_tokens = await client.query_json_rows(sql_tokens)
        token_data = result_tokens['rows']

        if token_data:
            row = token_data[0]
            input_tokens = int(row.get('total_input') or 0)
            output_tokens = int(row.get('total_output') or 0)
            cost = calculate_cost("gpt-4o-mini", input_tokens, output_tokens)

            print(f"\n=== Cost Analysis (Q6) ===")
            print(f"Input tokens:  {input_tokens:,}")
            print(f"Output tokens: {output_tokens:,}")
            print(f"Total cost:    ${cost:.6f}")
        else:
            print("No token data found for this trace.")

        # Bonus: count positive vs negative feedback
        sql_feedback = """
            SELECT
                attributes->>'score' AS score,
                COUNT(*) AS count
            FROM records
            WHERE span_name = 'user_feedback'
            GROUP BY score
        """
        result_fb = await client.query_json_rows(sql_feedback)
        feedback_data = result_fb['rows']

        if feedback_data:
            print(f"\n=== Feedback Summary (Bonus) ===")
            for row in feedback_data:
                label = "👍 Positive" if str(row.get('score')) == '1' else "👎 Negative"
                print(f"{label}: {row['count']}")


if __name__ == "__main__":
    asyncio.run(get_session_traces())
