"""Tests for the MCP tool response."""

import unittest
from unittest.mock import AsyncMock, patch

from backend.mcp_server import ask_council


class AskCouncilTests(unittest.IsolatedAsyncioTestCase):
    async def test_returns_compact_result_by_default(self) -> None:
        council_result = (
            [{"model": "model-a", "response": "First opinion"}],
            [{"model": "model-a", "ranking": "FINAL RANKING: 1. Response A"}],
            {"model": "chairman", "response": "Final answer"},
            {
                "aggregate_rankings": [
                    {"model": "model-a", "average_rank": 1.0, "rankings_count": 1}
                ]
            },
        )

        with patch(
            "backend.mcp_server.run_full_council",
            new=AsyncMock(return_value=council_result),
        ):
            result = await ask_council("What should I do?")

        self.assertEqual(result["answer"], "Final answer")
        self.assertEqual(result["chairman_model"], "chairman")
        self.assertEqual(result["models_consulted"], 1)
        self.assertNotIn("individual_responses", result)
        self.assertNotIn("peer_reviews", result)

    async def test_includes_details_when_requested(self) -> None:
        stage1 = [{"model": "model-a", "response": "First opinion"}]
        stage2 = [{"model": "model-a", "ranking": "1. Response A"}]
        council_result = (
            stage1,
            stage2,
            {"model": "chairman", "response": "Final answer"},
            {"aggregate_rankings": []},
        )

        with patch(
            "backend.mcp_server.run_full_council",
            new=AsyncMock(return_value=council_result),
        ):
            result = await ask_council("Compare the options", include_details=True)

        self.assertEqual(result["individual_responses"], stage1)
        self.assertEqual(result["peer_reviews"], stage2)

    async def test_rejects_an_empty_question(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            await ask_council("   ")


if __name__ == "__main__":
    unittest.main()
