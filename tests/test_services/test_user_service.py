import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.services.user_service import UserService
from app.db.models import User

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for a test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_get_or_create_user(db_session):
    user_service = UserService(db_session)
    slack_user_id = "U12345"

    # First time, user should be created
    user1 = user_service.get_or_create_user(slack_user_id)
    assert user1.slack_user_id == slack_user_id
    assert user1.id is not None

    # Second time, existing user should be returned
    user2 = user_service.get_or_create_user(slack_user_id)
    assert user2.id == user1.id


def test_update_api_key(db_session):
    user_service = UserService(db_session)
    slack_user_id = "U12345"
    api_key = "test_api_key"

    user = user_service.update_api_key(slack_user_id, api_key)
    assert user.api_key == api_key

    # Verify that the user was created if they didn't exist
    fetched_user = (
        db_session.query(User).filter(User.slack_user_id == slack_user_id).first()
    )
    assert fetched_user is not None
    assert fetched_user.api_key == api_key
