import pytest
from unittest.mock import AsyncMock, MagicMock
from app.bot.commands import (
    summarize_text_command,
)  # Directly import the command handler
from app.services.ai_service import AIService


@pytest.fixture
def mock_ai_service():
    """Mock AIService instance."""
    service = MagicMock(spec=AIService)
    service.summarize_text = AsyncMock(return_value="요약된 텍스트입니다.")
    return service


@pytest.fixture
def mock_say():
    """Mock 'say' function from Slack Bolt context."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_summarize_command_success(mock_ai_service, mock_say):
    """
    Test that the /요약 command successfully summarizes text and responds.
    """
    command_payload = {
        "text": "이것은 요약할 긴 텍스트입니다. 이 텍스트는 AI 서비스에 의해 요약될 것입니다."
    }

    await summarize_text_command(
        ack=AsyncMock(),
        say=mock_say,
        command=command_payload,
        ai_service=mock_ai_service,
    )

    # Assertions
    mock_ai_service.summarize_text.assert_called_once_with(
        "이것은 요약할 긴 텍스트입니다. 이 텍스트는 AI 서비스에 의해 요약될 것입니다."
    )
    mock_say.assert_called_once_with("요약 결과:\n요약된 텍스트입니다.")


@pytest.mark.asyncio
async def test_summarize_command_no_text(mock_ai_service, mock_say):
    """
    Test that the /요약 command handles empty text input.
    """
    command_payload = {"text": ""}

    await summarize_text_command(
        ack=AsyncMock(),
        say=mock_say,
        command=command_payload,
        ai_service=mock_ai_service,
    )

    # Assertions
    mock_ai_service.summarize_text.assert_not_called()
    mock_say.assert_called_once_with(
        "요약할 텍스트를 입력해주세요. 예: `/요약 긴 텍스트...`"
    )


@pytest.mark.asyncio
async def test_summarize_command_ai_service_error(mock_ai_service, mock_say):
    """
    Test that the /요약 command handles errors from AIService.
    """
    # Configure mock_ai_service to raise an exception
    mock_ai_service.summarize_text.side_effect = Exception("API 호출 실패")

    command_payload = {"text": "이것은 요약할 텍스트입니다."}

    await summarize_text_command(
        ack=AsyncMock(),
        say=mock_say,
        command=command_payload,
        ai_service=mock_ai_service,
    )

    # Assertions
    mock_ai_service.summarize_text.assert_called_once()
    mock_say.assert_called_once_with(
        "텍스트 요약 중 오류가 발생했습니다: API 호출 실패"
    )
