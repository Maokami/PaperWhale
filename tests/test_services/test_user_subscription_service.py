import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services.user_subscription_service import UserSubscriptionService
from app.db.models import User, Keyword, UserKeyword, Author, UserAuthor
from app.services.user_service import UserService


@pytest.fixture
def mock_db_session():
    mock_session = MagicMock(spec=Session)
    # Ensure query().filter() returns a mock that has .first() and .all()
    mock_session.query.return_value.filter.return_value = MagicMock()
    return mock_session


@pytest.fixture
def mock_user_service():
    mock_service = MagicMock(spec=UserService)
    mock_service.get_or_create_user.return_value = User(id=1, slack_user_id="U123")
    return mock_service


@pytest.fixture
def user_subscription_service(mock_db_session, mock_user_service):
    # Reset mock_db_session for each test to ensure clean state
    mock_db_session.reset_mock()
    mock_db_session.query.return_value.filter.return_value = (
        MagicMock()
    )  # Re-mock the chain

    service = UserSubscriptionService(mock_db_session)
    service.user_service = mock_user_service  # Inject the mocked user_service
    return service


def test_subscribe_keyword_new_keyword(user_subscription_service, mock_db_session):
    # Mock for Keyword.first() and UserKeyword.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        None,
        None,
    ]

    result = user_subscription_service.subscribe_keyword("U123", "new_keyword")

    assert result is not None
    assert isinstance(result, UserKeyword)
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_subscribe_keyword_existing_keyword(user_subscription_service, mock_db_session):
    existing_keyword = Keyword(id=1, name="existing_keyword")
    # Mock for Keyword.first() and UserKeyword.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_keyword,
        None,
    ]

    result = user_subscription_service.subscribe_keyword("U123", "existing_keyword")

    assert result is not None
    assert isinstance(result, UserKeyword)
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_subscribe_keyword_already_subscribed(
    user_subscription_service, mock_db_session
):
    existing_keyword = Keyword(id=1, name="existing_keyword")
    existing_user_keyword = UserKeyword(user_id=1, keyword_id=1)
    # Mock for Keyword.first() and UserKeyword.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_keyword,
        existing_user_keyword,
    ]

    result = user_subscription_service.subscribe_keyword("U123", "existing_keyword")

    assert result is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()


def test_unsubscribe_keyword_success(user_subscription_service, mock_db_session):
    existing_keyword = Keyword(id=1, name="existing_keyword")
    existing_user_keyword = UserKeyword(user_id=1, keyword_id=1)
    # Mock for Keyword.first() and UserKeyword.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_keyword,
        existing_user_keyword,
    ]

    result = user_subscription_service.unsubscribe_keyword("U123", "existing_keyword")

    assert result is True
    mock_db_session.delete.assert_called_once_with(existing_user_keyword)
    mock_db_session.commit.assert_called_once()


def test_unsubscribe_keyword_not_found(user_subscription_service, mock_db_session):
    # Mock for Keyword.first()
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = user_subscription_service.unsubscribe_keyword(
        "U123", "non_existent_keyword"
    )

    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_unsubscribe_keyword_not_subscribed(user_subscription_service, mock_db_session):
    existing_keyword = Keyword(id=1, name="existing_keyword")
    # Mock for Keyword.first() and UserKeyword.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_keyword,
        None,
    ]

    result = user_subscription_service.unsubscribe_keyword("U123", "existing_keyword")

    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_get_user_keywords(user_subscription_service, mock_db_session):
    mock_user_keyword = MagicMock(spec=UserKeyword)
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        mock_user_keyword
    ]

    result = user_subscription_service.get_user_keywords("U123")

    assert len(result) == 1
    assert result[0] == mock_user_keyword


def test_subscribe_author_new_author(user_subscription_service, mock_db_session):
    # Mock for Author.first() and UserAuthor.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        None,
        None,
    ]

    result = user_subscription_service.subscribe_author("U123", "new_author")

    assert result is not None
    assert isinstance(result, UserAuthor)
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_subscribe_author_existing_author(user_subscription_service, mock_db_session):
    existing_author = Author(id=1, name="existing_author")
    # Mock for Author.first() and UserAuthor.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_author,
        None,
    ]

    result = user_subscription_service.subscribe_author("U123", "existing_author")

    assert result is not None
    assert isinstance(result, UserAuthor)
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_subscribe_author_already_subscribed(
    user_subscription_service, mock_db_session
):
    existing_author = Author(id=1, name="existing_author")
    existing_user_author = UserAuthor(user_id=1, author_id=1)
    # Mock for Author.first() and UserAuthor.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_author,
        existing_user_author,
    ]

    result = user_subscription_service.subscribe_author("U123", "existing_author")

    assert result is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()


def test_unsubscribe_author_success(user_subscription_service, mock_db_session):
    existing_author = Author(id=1, name="existing_author")
    existing_user_author = UserAuthor(user_id=1, author_id=1)
    # Mock for Author.first() and UserAuthor.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_author,
        existing_user_author,
    ]

    result = user_subscription_service.unsubscribe_author("U123", "existing_author")

    assert result is True
    mock_db_session.delete.assert_called_once_with(existing_user_author)
    mock_db_session.commit.assert_called_once()


def test_unsubscribe_author_not_found(user_subscription_service, mock_db_session):
    # Mock for Author.first()
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    result = user_subscription_service.unsubscribe_author("U123", "non_existent_author")

    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_unsubscribe_author_not_subscribed(user_subscription_service, mock_db_session):
    existing_author = Author(id=1, name="existing_author")
    # Mock for Author.first() and UserAuthor.first()
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        existing_author,
        None,
    ]

    result = user_subscription_service.unsubscribe_author("U123", "existing_author")

    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_get_user_authors(user_subscription_service, mock_db_session):
    mock_user_author = MagicMock(spec=UserAuthor)
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        mock_user_author
    ]

    result = user_subscription_service.get_user_authors("U123")

    assert len(result) == 1
    assert result[0] == mock_user_author
