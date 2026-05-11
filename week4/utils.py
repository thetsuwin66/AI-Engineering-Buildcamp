from pydantic_ai.messages import ToolCallPart


def collect_tools(messages) -> list[str]:
    """Extract tool call names in order from agent message history."""
    tool_calls = []
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                tool_calls.append(part.tool_name)
    return tool_calls
