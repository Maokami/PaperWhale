import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.ai_service import AIService
from tenacity import RetryError
from contextlib import ExitStack


@pytest.fixture
def ai_service():
    return AIService(api_key="test_api_key")


@pytest.mark.asyncio
async def test_summarize_text_success(ai_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Summarized text."

    with patch("openai.ChatCompletion.acreate", new_callable=AsyncMock) as mock_acreate:
        mock_acreate.return_value = mock_response
        summary = await ai_service.summarize_text("This is a test text.")

        assert summary == "Summarized text."
        mock_acreate.assert_called_once()


@pytest.mark.asyncio
async def test_summarize_text_exception(ai_service):
    with ExitStack() as stack:
        mock_acreate = stack.enter_context(
            patch("openai.ChatCompletion.acreate", new_callable=AsyncMock)
        )
        mock_print = stack.enter_context(patch("builtins.print"))

        mock_acreate.side_effect = Exception("OpenAI error")

        with pytest.raises(RetryError) as excinfo:
            await ai_service.summarize_text("This is a test text.")

        assert "OpenAI error" in str(excinfo.value.last_attempt.exception())
        # Check the arguments of the last call
        assert mock_acreate.call_args.kwargs["model"] == "gpt-3.5-turbo"
        assert mock_acreate.call_args.kwargs["messages"] == [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes academic papers.",
            },
            {
                "role": "user",
                "content": "Please summarize the following text: \n\nThis is a test text.",
            },
        ]
        # The mock_acreate is called multiple times due to retry, so we check the last call
        assert mock_acreate.call_count == 5  # Default stop_after_attempt is 5
        assert mock_print.call_count == 5  # print is called on each retry attempt
        mock_print.assert_called_with("Error during summarization: OpenAI error")
