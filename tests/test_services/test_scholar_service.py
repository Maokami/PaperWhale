import pytest
from unittest.mock import MagicMock, patch
from app.services.scholar_service import ScholarService


@pytest.fixture
def scholar_service():
    return ScholarService()


def test_search_new_papers_success(scholar_service):
    mock_author_one = MagicMock()
    mock_author_one.name = "Author One"
    mock_author_two = MagicMock()
    mock_author_two.name = "Author Two"

    mock_result = MagicMock()
    mock_result.title = "Test Paper Title"
    mock_result.pdf_url = "http://example.com/test.pdf"
    mock_result.summary = "This is a test summary."
    mock_result.authors = [mock_author_one, mock_author_two]
    mock_result.published = "2023-01-01"
    mock_result.entry_id = "http://arxiv.org/abs/2301.00001v1"

    with patch(
        "arxiv.Client.results", return_value=[mock_result]
    ) as mock_arxiv_results:
        papers = scholar_service.search_new_papers("test_keyword")

        assert len(papers) == 1
        assert papers[0]["title"] == "Test Paper Title"
        assert papers[0]["url"] == "http://example.com/test.pdf"
        assert papers[0]["summary"] == "This is a test summary."
        assert papers[0]["authors"] == ["Author One", "Author Two"]
        assert papers[0]["published_date"] == "2023-01-01"
        assert papers[0]["arxiv_id"] == "2301.00001v1"
        mock_arxiv_results.assert_called_once()


def test_search_new_papers_exception(scholar_service):
    with patch(
        "arxiv.Client.results", side_effect=Exception("ArXiv error")
    ) as mock_arxiv_results:
        with patch("app.services.scholar_service.logger.error") as mock_logger_error:
            papers = scholar_service.search_new_papers("test_keyword")

            assert len(papers) == 0
            mock_arxiv_results.assert_called_once()
            mock_logger_error.assert_called_once_with(
                "Error searching arXiv for keyword 'test_keyword': ArXiv error"
            )
