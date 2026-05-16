"""Utilities for fetching and reconstructing agent runs from Logfire traces."""
import json
from typing import Any
from logfire.query_client import AsyncLogfireQueryClient


async def fetch_trace(client: AsyncLogfireQueryClient, trace_id: str) -> list[dict]:
    """Fetch all spans for a given trace ID from Logfire."""
    sql = f"""
        SELECT
            span_id,
            parent_span_id,
            span_name,
            start_timestamp,
            end_timestamp,
            attributes,
            tags
        FROM records
        WHERE trace_id = '{trace_id}'
        ORDER BY start_timestamp
    """
    result = await client.query_json(sql)
    rows = json.loads(result)
    return rows


async def reconstruct_messages(client: AsyncLogfireQueryClient, trace_id: str) -> list[dict]:
    """Reconstruct agent message history from a Logfire trace."""
    spans = await fetch_trace(client, trace_id)

    messages = []
    for span in spans:
        attrs = span.get('attributes', {})
        if isinstance(attrs, str):
            try:
                attrs = json.loads(attrs)
            except (json.JSONDecodeError, TypeError):
                attrs = {}

        # Extract messages stored in gen_ai spans
        if 'gen_ai.prompt' in attrs:
            try:
                prompt_data = json.loads(attrs['gen_ai.prompt'])
                if isinstance(prompt_data, list):
                    messages.extend(prompt_data)
            except (json.JSONDecodeError, TypeError):
                pass

    return messages


def get_token_counts(spans: list[dict]) -> dict[str, int]:
    """Sum up input/output tokens across all spans in a trace."""
    total_input = 0
    total_output = 0

    for span in spans:
        attrs = span.get('attributes', {})
        if isinstance(attrs, str):
            try:
                attrs = json.loads(attrs)
            except (json.JSONDecodeError, TypeError):
                attrs = {}

        total_input += attrs.get('gen_ai.usage.input_tokens', 0) or 0
        total_output += attrs.get('gen_ai.usage.output_tokens', 0) or 0

    return {'input_tokens': total_input, 'output_tokens': total_output}
