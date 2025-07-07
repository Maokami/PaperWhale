import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, User, Paper
from app.services.paper_service import PaperService
from app.services.user_service import UserService
from app.bot.actions import _process_add_paper_submission

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def paper_service(db_session):
    svc = PaperService(db_session)
    svc.get_paper_by_url_or_arxiv_id = MagicMock(return_value=None)
    return svc


@pytest.fixture(scope="function")
def user_service(db_session):
    return UserService(db_session)


@pytest.fixture
def mock_slack_context():
    ack = AsyncMock()
    client = MagicMock()
    client.chat_postMessage = AsyncMock()
    logger = MagicMock()
    return ack, client, logger


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_bibtex_only(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    # Mock PaperService.create_paper to return a dummy paper
    paper_service.create_paper = MagicMock(
        return_value=Paper(
            id=1, title="Test BibTeX Paper", url="http://example.com/bibtex"
        )
    )

    # Mock UserService.get_or_create_user
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    # BibTeX string for testing
    bibtex_str = """
@article{test2023bibtex,
  title={Test BibTeX Paper},
  author={Doe, John and Smith, Jane},
  journal={Journal of Testing},
  year={2023},
  url={http://example.com/bibtex},
  eprint={2301.00001}
}
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": bibtex_str}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    # Assertions
    ack.assert_called_once()
    client.chat_postMessage.assert_called_once_with(
        channel="U123",
        text="Paper 'Test BibTeX Paper' successfully added. To enable AI summarization, please register your OpenAI API key.",
    )
    paper_service.create_paper.assert_called_once()
    args, _ = paper_service.create_paper.call_args
    created_paper_data = args[0]
    assert created_paper_data.title == "Test BibTeX Paper"
    assert str(created_paper_data.url) == "http://example.com/bibtex"
    assert "John Doe" in created_paper_data.author_names
    assert created_paper_data.published_date.year == 2023
    assert created_paper_data.arxiv_id == "2301.00001"
    assert created_paper_data.bibtex == bibtex_str


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_manual_input_only(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    paper_service.create_paper = MagicMock(
        return_value=Paper(id=2, title="Manual Paper", url="http://manual.com")
    )
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {
                        "paper_title_input": {"value": "Manual Paper"}
                    },
                    "paper_url_block": {
                        "paper_url_input": {"value": "http://manual.com"}
                    },
                    "paper_authors_block": {
                        "paper_authors_input": {"value": "Author One"}
                    },
                    "paper_keywords_block": {
                        "paper_keywords_input": {"value": "Manual, Input"}
                    },
                    "paper_summary_block": {
                        "paper_summary_input": {"value": "This is a manual summary."}
                    },
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": "2024-01-01"}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": ""}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    client.chat_postMessage.assert_called_once_with(
        channel="U123", text="Paper 'Manual Paper' successfully added!"
    )
    paper_service.create_paper.assert_called_once()
    args, _ = paper_service.create_paper.call_args
    created_paper_data = args[0]
    assert created_paper_data.title == "Manual Paper"
    assert str(created_paper_data.url) == "http://manual.com"
    assert "Author One" in created_paper_data.author_names
    assert created_paper_data.published_date.year == 2024
    assert created_paper_data.bibtex == ""


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_bibtex_and_manual_override(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    paper_service.create_paper = MagicMock(
        return_value=Paper(id=3, title="Overridden Title", url="http://overridden.com")
    )
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    bibtex_str = """
@article{original2022paper,
  title={Original BibTeX Title},
  author={Original Author},
  journal={Original Journal},
  year={2022},
  url={http://original.com},
  eprint={2201.00001}
}
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {
                        "paper_title_input": {"value": "Overridden Title"}
                    },
                    "paper_url_block": {
                        "paper_url_input": {"value": "http://overridden.com"}
                    },
                    "paper_authors_block": {
                        "paper_authors_input": {"value": "Manual Author"}
                    },  # Manual authors should override
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": "2024-02-02"}
                    },  # Manual date should override
                    "paper_arxiv_id_block": {
                        "paper_arxiv_id_input": {"value": "2401.00001"}
                    },  # Manual arxiv_id should override
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": bibtex_str}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    client.chat_postMessage.assert_called_once_with(
        channel="U123",
        text="Paper 'Overridden Title' successfully added. To enable AI summarization, please register your OpenAI API key.",
    )
    paper_service.create_paper.assert_called_once()
    args, _ = paper_service.create_paper.call_args
    created_paper_data = args[0]
    assert created_paper_data.title == "Overridden Title"
    assert str(created_paper_data.url) == "http://overridden.com"
    assert "Manual Author" in created_paper_data.author_names
    assert created_paper_data.published_date.year == 2024
    assert created_paper_data.published_date.month == 2
    assert created_paper_data.published_date.day == 2
    assert created_paper_data.arxiv_id == "2401.00001"
    assert created_paper_data.bibtex == bibtex_str


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_invalid_bibtex(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    invalid_bibtex_str = """
This is not a valid bibtex entry.
@article{
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {
                        "paper_bibtex_input": {"value": invalid_bibtex_str}
                    },
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once_with(
        response_action="errors",
        errors={
            "paper_bibtex_block": "BibTeX 파싱 오류: Expecting an entry, got 'This is not a valid bibtex entry.\n@article{'"
        },
    )
    client.chat_postMessage.assert_not_called()
    paper_service.create_paper.assert_not_called()


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_missing_required_fields(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    # Neither BibTeX nor title/URL provided
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": ""}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    args, kwargs = ack.call_args
    assert kwargs["response_action"] == "errors"
    assert "paper_title_block" in kwargs["errors"]
    assert (
        "Either bibtex must be provided, or both title and url must be provided."
        in kwargs["errors"]["paper_title_block"]
    )
    client.chat_postMessage.assert_not_called()
    paper_service.create_paper.assert_not_called()


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_bibtex_minimal_fields(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    paper_service.create_paper = MagicMock(
        return_value=Paper(id=4, title="Minimal BibTeX", url="http://minimal.com")
    )
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    bibtex_str = """
@article{minimal2023,
  title={Minimal BibTeX},
  author={First Author},
  year={2023},
  url={http://minimal.com}
}
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": bibtex_str}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    client.chat_postMessage.assert_called_once_with(
        channel="U123", text="Paper 'Minimal BibTeX' successfully added!"
    )
    paper_service.create_paper.assert_called_once()
    args, _ = paper_service.create_paper.call_args
    created_paper_data = args[0]
    assert created_paper_data.title == "Minimal BibTeX"
    assert str(created_paper_data.url) == "http://minimal.com"
    assert "First Author" in created_paper_data.author_names
    assert created_paper_data.published_date.year == 2023
    assert created_paper_data.arxiv_id is None
    assert created_paper_data.bibtex == bibtex_str


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_bibtex_no_url_or_arxiv_id(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    paper_service.create_paper = MagicMock(
        return_value=Paper(
            id=5, title="No URL BibTeX", url="http://example.com/default"
        )
    )
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    bibtex_str = """
@article{nourl2023,
  title={No URL BibTeX},
  author={Test Author},
  year={2023}
}
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": bibtex_str}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    # Expecting an error because neither manual URL nor BibTeX URL/eprint is provided
    args, kwargs = ack.call_args
    assert kwargs["response_action"] == "errors"
    assert "paper_title_block" in kwargs["errors"]
    assert (
        "Either bibtex must be provided, or both title and url must be provided."
        in kwargs["errors"]["paper_title_block"]
    )
    client.chat_postMessage.assert_not_called()
    paper_service.create_paper.assert_not_called()


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_bibtex_only_eprint(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    paper_service.create_paper = MagicMock(
        return_value=Paper(
            id=6, title="Eprint Only", url="http://arxiv.org/pdf/2304.00001"
        )
    )
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    bibtex_str = """
@article{eprint2023,
  title={Eprint Only},
  author={Eprint Author},
  year={2023},
  eprint={2304.00001}
}
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": bibtex_str}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    client.chat_postMessage.assert_called_once_with(
        channel="U123",
        text="Paper 'Eprint Only' successfully added. To enable AI summarization, please register your OpenAI API key.",
    )
    paper_service.create_paper.assert_called_once()
    args, _ = paper_service.create_paper.call_args
    created_paper_data = args[0]
    assert created_paper_data.title == "Eprint Only"
    assert "arxiv.org/pdf/2304.00001" in str(created_paper_data.url)
    assert created_paper_data.arxiv_id == "2304.00001"
    assert created_paper_data.bibtex == bibtex_str


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_bibtex_invalid_year(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    paper_service.create_paper = MagicMock(
        return_value=Paper(
            id=7, title="Invalid Year BibTeX", url="http://invalidyear.com"
        )
    )
    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    bibtex_str = """
@article{invalidyear2023,
  title={Invalid Year BibTeX},
  author={Year Author},
  year={not-a-year},
  url={http://invalidyear.com}
}
"""
    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": ""}},
                    "paper_url_block": {"paper_url_input": {"value": ""}},
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": bibtex_str}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once()
    client.chat_postMessage.assert_called_once_with(
        channel="U123",
        text="Paper 'Invalid Year BibTeX' successfully added!",
    )
    paper_service.create_paper.assert_called_once()
    args, _ = paper_service.create_paper.call_args
    created_paper_data = args[0]
    assert created_paper_data.title == "Invalid Year BibTeX"
    assert str(created_paper_data.url) == "http://invalidyear.com"
    assert (
        created_paper_data.published_date is not None
    )  # Should default to current datetime if year parsing fails
    assert created_paper_data.bibtex == bibtex_str


@pytest.mark.asyncio
@patch("app.db.database.get_db")
async def test_add_paper_with_existing_url(
    mock_get_db, db_session, paper_service, user_service, mock_slack_context
):
    ack, client, logger = mock_slack_context
    mock_get_db.return_value = iter([db_session])

    # Mock an existing paper
    existing_paper = Paper(
        id=99, title="Existing Paper", url="http://existing.com", arxiv_id="9999.99999"
    )
    paper_service.get_paper_by_url_or_arxiv_id = MagicMock(return_value=existing_paper)
    # Ensure create_paper is not called
    paper_service.create_paper = MagicMock()

    user_service.get_or_create_user = MagicMock(
        return_value=User(id=1, slack_user_id="U123")
    )

    body = {
        "user": {"id": "U123"},
        "view": {
            "state": {
                "values": {
                    "paper_title_block": {"paper_title_input": {"value": "New Paper"}},
                    "paper_url_block": {
                        "paper_url_input": {"value": "http://existing.com"}
                    },
                    "paper_authors_block": {"paper_authors_input": {"value": ""}},
                    "paper_keywords_block": {"paper_keywords_input": {"value": ""}},
                    "paper_summary_block": {"paper_summary_input": {"value": ""}},
                    "paper_published_date_block": {
                        "paper_published_date_input": {"value": ""}
                    },
                    "paper_arxiv_id_block": {"paper_arxiv_id_input": {"value": ""}},
                    "paper_bibtex_block": {"paper_bibtex_input": {"value": ""}},
                }
            }
        },
    }

    with (
        patch("app.services.paper_service.PaperService", return_value=paper_service),
        patch("app.services.user_service.UserService", return_value=user_service),
    ):
        await _process_add_paper_submission(
            ack, body, client, logger, db_session, paper_service, user_service
        )

    ack.assert_called_once_with(
        response_action="errors",
        errors={"paper_url_block": f"이미 존재하는 논문입니다: {existing_paper.title}"},
    )
    paper_service.get_paper_by_url_or_arxiv_id.assert_called_once_with(
        url="http://existing.com", arxiv_id=None
    )
    paper_service.create_paper.assert_not_called()
    client.chat_postMessage.assert_not_called()
