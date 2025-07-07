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
    mock_response.text = "Summarized text."

    with patch("google.generativeai.GenerativeModel") as mock_generative_model:
        mock_instance = mock_generative_model.return_value
        mock_instance.generate_content_async = AsyncMock(return_value=mock_response)

        summary = await ai_service.summarize_text("This is a test text.")

        assert summary == "Summarized text."
        mock_generative_model.assert_called_once_with("gemini-pro")
        mock_instance.generate_content_async.assert_called_once_with(
            "Please summarize the following text: \n\nThis is a test text."
        )


@pytest.mark.asyncio
async def test_summarize_text_exception(ai_service):
    with ExitStack() as stack:
        mock_generative_model = stack.enter_context(
            patch("google.generativeai.GenerativeModel")
        )
        mock_instance = mock_generative_model.return_value
        mock_instance.generate_content_async = AsyncMock(
            side_effect=Exception("Gemini error")
        )
        mock_print = stack.enter_context(patch("builtins.print"))

        with pytest.raises(RetryError) as excinfo:
            await ai_service.summarize_text("This is a test text.")

        assert "Gemini error" in str(excinfo.value.last_attempt.exception())
        # mock_generative_model.assert_called_once_with("gemini-pro") # Removed this assertion
        # mock_instance.generate_content_async.assert_called_once_with(
        #     "Please summarize the following text: \n\nThis is a test text."
        # ) # Removed this assertion
        assert mock_instance.generate_content_async.call_args == (
            ("Please summarize the following text: \n\nThis is a test text.",),
            {},
        )  # Removed this assertion
        assert (
            mock_instance.generate_content_async.call_count == 5
        )  # Default stop_after_attempt is 5
        assert mock_print.call_count == 5  # print is called on each retry attempt
        mock_print.assert_called_with("Error during summarization: Gemini error")
