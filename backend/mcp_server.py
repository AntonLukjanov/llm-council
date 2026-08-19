"""MCP server that exposes the LLM Council to ChatGPT and other MCP clients."""

import os
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .council import run_full_council


MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8002"))

mcp = FastMCP(
    name="LLM Council",
    instructions=(
        "Use ask_council when the user asks for a second opinion, comparison, "
        "or a carefully reviewed answer from several AI models."
    ),
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
)


@mcp.tool(
    title="Ask the LLM Council",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        openWorldHint=True,
    ),
)
async def ask_council(
    question: str,
    include_details: bool = False,
) -> Dict[str, Any]:
    """Ask several AI models, let them rank each other, and return a final answer.

    Args:
        question: The complete question to send to the LLM Council.
        include_details: Include every model response and peer review when true.

    Returns:
        The chairman's final answer, aggregate rankings, and optional details.
    """
    question = question.strip()
    if not question:
        raise ValueError("question must not be empty")

    stage1, stage2, stage3, metadata = await run_full_council(question)

    result: Dict[str, Any] = {
        "answer": stage3.get("response", ""),
        "chairman_model": stage3.get("model", ""),
        "models_consulted": len(stage1),
        "aggregate_rankings": metadata.get("aggregate_rankings", []),
    }

    if include_details:
        result["individual_responses"] = stage1
        result["peer_reviews"] = stage2

    return result


def main() -> None:
    """Run the MCP server using Streamable HTTP transport."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
