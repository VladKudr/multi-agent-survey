"""Parser for LLM responses."""

import json
import re
from typing import Any

import structlog

from schemas.agent import AgentResponse

logger = structlog.get_logger()


class ResponseParseError(Exception):
    """Error parsing LLM response."""

    pass


class ResponseParser:
    """Parse LLM responses into structured formats."""

    @staticmethod
    def extract_json(text: str) -> dict[str, Any]:
        """Extract JSON from text, handling markdown code blocks."""
        # Try to find JSON in markdown code blocks
        patterns = [
            r"```json\s*(.*?)\s*```",  # ```json ... ```
            r"```\s*(.*?)\s*```",  # ``` ... ```
            r"(\{[\s\S]*\})",  # Any JSON-like object
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # Try parsing the entire text as JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        raise ResponseParseError(f"Could not extract valid JSON from: {text[:200]}...")

    @staticmethod
    def parse_quantitative_response(
        llm_response: str, agent_id: str
    ) -> AgentResponse:
        """Parse quantitative response with numeric value."""
        try:
            data = ResponseParser.extract_json(llm_response)

            reasoning = data.get("reasoning", "")
            response_value = data.get("response_value")

            if response_value is None:
                raise ResponseParseError("Missing 'response_value' in response")

            # Validate value is numeric
            try:
                response_value = float(response_value)
            except (ValueError, TypeError):
                raise ResponseParseError(f"Invalid numeric value: {response_value}")

            return AgentResponse(
                agent_id=agent_id,
                response_type="quantitative",
                response_value=response_value,
                reasoning=reasoning,
                tokens_used=0,  # Will be set by caller
                response_time_ms=0,  # Will be set by caller
            )

        except Exception as e:
            logger.error(
                "parse_quantitative_failed",
                agent_id=agent_id,
                error=str(e),
                response_preview=llm_response[:200],
            )
            raise ResponseParseError(f"Failed to parse quantitative response: {e}")

    @staticmethod
    def parse_qualitative_response(
        llm_response: str, agent_id: str
    ) -> AgentResponse:
        """Parse qualitative response with free text."""
        try:
            data = ResponseParser.extract_json(llm_response)

            reasoning = data.get("reasoning", "")
            answer_text = data.get("answer_text")

            if not answer_text:
                raise ResponseParseError("Missing 'answer_text' in response")

            return AgentResponse(
                agent_id=agent_id,
                response_type="qualitative",
                reasoning=reasoning,
                answer_text=answer_text,
                tokens_used=0,  # Will be set by caller
                response_time_ms=0,  # Will be set by caller
            )

        except Exception as e:
            logger.error(
                "parse_qualitative_failed",
                agent_id=agent_id,
                error=str(e),
                response_preview=llm_response[:200],
            )
            raise ResponseParseError(f"Failed to parse qualitative response: {e}")

    @staticmethod
    def estimate_word_count(text: str) -> int:
        """Estimate word count in text."""
        # Simple word counting for Cyrillic and Latin
        words = re.findall(r"\b\w+\b", text)
        return len(words)

    @staticmethod
    def validate_qualitative_length(
        answer_text: str, min_words: int, max_words: int
    ) -> bool:
        """Validate qualitative response length."""
        word_count = ResponseParser.estimate_word_count(answer_text)
        return min_words <= word_count <= max_words
