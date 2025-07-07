import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.core.scheduler import (
    start_scheduler,
    shutdown_scheduler,
    check_for_new_papers_async,
)
from app.db.models import Keyword, Paper, Author
from datetime import datetime
from contextlib import ExitStack


@pytest.fixture
def mock_scheduler():
    with patch("app.core.scheduler.scheduler") as mock:
        yield mock


@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = []  # Default for all()
    mock_query.first.return_value = None  # Default for first()
    return mock_session


@pytest.fixture
def mock_scholar_service_instance():
    return MagicMock()


@pytest.fixture
def mock_slack_service_instance():
    return AsyncMock()


@pytest.fixture
def mock_paper_service_instance():
    return MagicMock()


@pytest.mark.asyncio
async def test_start_scheduler(mock_scheduler):
    await start_scheduler()
    mock_scheduler.start.assert_called_once()
    mock_scheduler.add_job.assert_called_once_with(
        check_for_new_papers_async,
        "interval",
        minutes=60,
        id="new_paper_check",
        replace_existing=True,
    )


@pytest.mark.asyncio
async def test_shutdown_scheduler(mock_scheduler):
    await shutdown_scheduler()
    mock_scheduler.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_check_for_new_papers_async_new_paper(
    mock_db_session,
    mock_scholar_service_instance,
    mock_slack_service_instance,
    mock_paper_service_instance,
):
    # Mock data
    user_keyword = MagicMock()
    user_keyword.user = MagicMock(slack_user_id="U123")
    user_keyword.keyword.name = "test_keyword"
    mock_db_session.query().all.return_value = [user_keyword]

    mock_scholar_service_instance.search_new_papers.return_value = [
        {
            "title": "New Paper",
            "url": "http://new.com",
            "summary": "Summary of new paper",
            "authors": ["Author One"],
            "published_date": datetime.now(),
            "arxiv_id": "1234.56789",
        }
    ]

    mock_paper_service_instance.create_paper.return_value = Paper(
        id=1,
        title="New Paper",
        url="http://new.com",
        summary="Summary of new paper",
        published_date=datetime.now(),
        arxiv_id="1234.56789",
        authors=[Author(name="Author One")],
        keywords=[Keyword(name="test_keyword")],
    )

    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "app.core.scheduler.ScholarService",
                return_value=mock_scholar_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.SlackService",
                return_value=mock_slack_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.PaperService",
                return_value=mock_paper_service_instance,
            )
        )
        stack.enter_context(
            patch("app.core.scheduler.SessionLocal", return_value=mock_db_session)
        )
        await check_for_new_papers_async()

        mock_scholar_service_instance.search_new_papers.assert_called_once_with(
            "test_keyword"
        )
        mock_paper_service_instance.create_paper.assert_called_once()
        mock_slack_service_instance.send_new_paper_notification.assert_called_once()
        mock_db_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_for_new_papers_async_existing_paper(
    mock_db_session,
    mock_scholar_service_instance,
    mock_slack_service_instance,
    mock_paper_service_instance,
):
    user_keyword = MagicMock()
    user_keyword.user = MagicMock(slack_user_id="U123")
    user_keyword.keyword.name = "test_keyword"
    mock_db_session.query().all.return_value = [user_keyword]

    mock_scholar_service_instance.search_new_papers.return_value = [
        {
            "title": "Existing Paper",
            "url": "http://existing.com",
            "summary": "Summary of existing paper",
            "authors": ["Author One"],
            "published_date": datetime.now(),
            "arxiv_id": "9876.54321",
        }
    ]

    mock_db_session.query().filter().first.return_value = Paper(
        id=1, title="Existing Paper"
    )  # Simulate existing paper

    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "app.core.scheduler.ScholarService",
                return_value=mock_scholar_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.SlackService",
                return_value=mock_slack_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.PaperService",
                return_value=mock_paper_service_instance,
            )
        )
        stack.enter_context(
            patch("app.core.scheduler.SessionLocal", return_value=mock_db_session)
        )
        await check_for_new_papers_async()

        mock_scholar_service_instance.search_new_papers.assert_called_once_with(
            "test_keyword"
        )
        mock_paper_service_instance.create_paper.assert_not_called()
        mock_slack_service_instance.send_new_paper_notification.assert_not_called()
        mock_db_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_for_new_papers_async_scholar_service_exception(
    mock_db_session,
    mock_scholar_service_instance,
    mock_slack_service_instance,
    mock_paper_service_instance,
):
    user_keyword = MagicMock()
    user_keyword.user = MagicMock(slack_user_id="U123")
    user_keyword.keyword.name = "test_keyword"
    mock_db_session.query().all.return_value = [user_keyword]

    mock_scholar_service_instance.search_new_papers.side_effect = Exception(
        "Scholar service error"
    )

    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "app.core.scheduler.ScholarService",
                return_value=mock_scholar_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.SlackService",
                return_value=mock_slack_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.PaperService",
                return_value=mock_paper_service_instance,
            )
        )
        stack.enter_context(
            patch("app.core.scheduler.SessionLocal", return_value=mock_db_session)
        )
        mock_print = stack.enter_context(
            patch("app.core.scheduler.print")
        )  # Patch print for error logging
        with pytest.raises(Exception):
            await check_for_new_papers_async()

        mock_scholar_service_instance.search_new_papers.assert_called_once()
        mock_paper_service_instance.create_paper.assert_not_called()
        mock_slack_service_instance.send_new_paper_notification.assert_not_called()
        mock_db_session.close.assert_called_once()
        mock_print.assert_called_once()  # Check that the error was printed


@pytest.mark.asyncio
async def test_check_for_new_papers_async_slack_notification_exception(
    mock_db_session,
    mock_scholar_service_instance,
    mock_slack_service_instance,
    mock_paper_service_instance,
):
    user_keyword = MagicMock()
    user_keyword.user = MagicMock(slack_user_id="U123")
    user_keyword.keyword.name = "test_keyword"
    mock_db_session.query().all.return_value = [user_keyword]

    mock_scholar_service_instance.search_new_papers.return_value = [
        {
            "title": "New Paper",
            "url": "http://new.com",
            "summary": "Summary of new paper",
            "authors": ["Author One"],
            "published_date": datetime.now(),
            "arxiv_id": "1234.56789",
        }
    ]

    mock_paper_service_instance.create_paper.return_value = Paper(
        id=1,
        title="New Paper",
        url="http://new.com",
        summary="Summary of new paper",
        published_date=datetime.now(),
        arxiv_id="1234.56789",
        authors=[Author(name="Author One")],
        keywords=[Keyword(name="test_keyword")],
    )

    mock_slack_service_instance.send_new_paper_notification.side_effect = Exception(
        "Slack notification error"
    )

    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "app.core.scheduler.ScholarService",
                return_value=mock_scholar_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.SlackService",
                return_value=mock_slack_service_instance,
            )
        )
        stack.enter_context(
            patch(
                "app.core.scheduler.PaperService",
                return_value=mock_paper_service_instance,
            )
        )
        stack.enter_context(
            patch("app.core.scheduler.SessionLocal", return_value=mock_db_session)
        )
        mock_print = stack.enter_context(
            patch("app.core.scheduler.print")
        )  # Patch print for error logging
        with pytest.raises(Exception):
            await check_for_new_papers_async()

        mock_scholar_service_instance.search_new_papers.assert_called_once()
        mock_paper_service_instance.create_paper.assert_called_once()
        mock_slack_service_instance.send_new_paper_notification.assert_called_once()
        mock_db_session.close.assert_called_once()
        mock_print.assert_called_once()  # Check that the error was printed
