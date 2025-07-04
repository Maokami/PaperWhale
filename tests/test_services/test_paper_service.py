import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.services.paper_service import PaperService
from app.db.schemas import PaperCreate, PaperUpdate
from datetime import datetime

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sql_app.db"

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
    return PaperService(db_session)

def test_create_paper(paper_service):
    paper_data = PaperCreate(
        title="Test Paper 1",
        url="http://example.com/paper1",
        summary="This is a test summary.",
        published_date=datetime(2023, 1, 1),
        arxiv_id="2301.00001",
        author_names=["John Doe", "Jane Smith"],
        keyword_names=["PL", "Testing"]
    )
    paper = paper_service.create_paper(paper_data)

    assert paper.id is not None
    assert paper.title == "Test Paper 1"
    assert paper.url == "http://example.com/paper1"
    assert len(paper.authors) == 2
    assert paper.authors[0].name == "John Doe"
    assert len(paper.keywords) == 2
    assert paper.keywords[0].name == "PL"

def test_get_paper(paper_service):
    paper_data = PaperCreate(
        title="Test Paper 2",
        url="http://example.com/paper2",
        summary="Another test summary.",
        published_date=datetime(2023, 2, 1),
        arxiv_id="2302.00002",
        author_names=["Alice"],
        keyword_names=["AI"]
    )
    created_paper = paper_service.create_paper(paper_data)

    fetched_paper = paper_service.get_paper(created_paper.id)
    assert fetched_paper is not None
    assert fetched_paper.title == "Test Paper 2"

def test_get_papers(paper_service):
    paper_service.create_paper(PaperCreate(title="Paper A", url="http://a.com"))
    paper_service.create_paper(PaperCreate(title="Paper B", url="http://b.com"))
    papers = paper_service.get_papers()
    assert len(papers) == 2

def test_update_paper(paper_service):
    paper_data = PaperCreate(
        title="Original Title",
        url="http://original.com",
        author_names=["Author1"],
        keyword_names=["Keyword1"]
    )
    created_paper = paper_service.create_paper(paper_data)

    update_data = PaperUpdate(
        title="Updated Title",
        summary="New summary.",
        author_names=["Author2", "Author3"],
        keyword_names=["Keyword2"]
    )
    updated_paper = paper_service.update_paper(created_paper.id, update_data)

    assert updated_paper.title == "Updated Title"
    assert updated_paper.summary == "New summary."
    assert len(updated_paper.authors) == 2
    assert updated_paper.authors[0].name == "Author2"
    assert len(updated_paper.keywords) == 1
    assert updated_paper.keywords[0].name == "Keyword2"

def test_delete_paper(paper_service):
    paper_data = PaperCreate(
        title="To Be Deleted",
        url="http://delete.com"
    )
    created_paper = paper_service.create_paper(paper_data)

    deleted = paper_service.delete_paper(created_paper.id)
    assert deleted is True
    assert paper_service.get_paper(created_paper.id) is None

def test_search_papers(paper_service):
    paper_service.create_paper(PaperCreate(title="Machine Learning in PL", url="http://ml.com", author_names=["John Doe"], keyword_names=["ML", "PL"])) 
    paper_service.create_paper(PaperCreate(title="Type Systems for AI", url="http://ts.com", author_names=["Jane Smith"], keyword_names=["AI", "Type Systems"])) 
    paper_service.create_paper(PaperCreate(title="Functional Programming", url="http://fp.com", author_names=["John Doe"], keyword_names=["FP"])) 

    results = paper_service.search_papers("PL")
    assert len(results) == 1
    assert results[0].title == "Machine Learning in PL"

    results = paper_service.search_papers("John Doe")
    assert len(results) == 2

    results = paper_service.search_papers("Type Systems")
    assert len(results) == 1
    assert results[0].title == "Type Systems for AI"

    results = paper_service.search_papers("NonExistent")
    assert len(results) == 0
