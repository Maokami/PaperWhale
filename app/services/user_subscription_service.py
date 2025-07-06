from sqlalchemy.orm import Session
from app.db.models import UserKeyword, UserAuthor, Keyword, Author
from app.db.schemas import UserKeywordCreate, UserAuthorCreate
from app.services.user_service import UserService
from typing import List, Optional


class UserSubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def subscribe_keyword(
        self, slack_user_id: str, keyword_name: str
    ) -> Optional[UserKeyword]:
        user = self.user_service.get_or_create_user(slack_user_id)
        keyword = self.db.query(Keyword).filter(Keyword.name == keyword_name).first()
        if not keyword:
            keyword = Keyword(name=keyword_name)
            self.db.add(keyword)
            self.db.flush()

        user_keyword = (
            self.db.query(UserKeyword)
            .filter(
                UserKeyword.user_id == user.id, UserKeyword.keyword_id == keyword.id
            )
            .first()
        )

        if user_keyword:
            return None  # Already subscribed

        new_user_keyword = UserKeyword(user_id=user.id, keyword_id=keyword.id)
        self.db.add(new_user_keyword)
        self.db.commit()
        self.db.refresh(new_user_keyword)
        return new_user_keyword

    def unsubscribe_keyword(self, slack_user_id: str, keyword_name: str) -> bool:
        user = self.user_service.get_or_create_user(slack_user_id)
        keyword = self.db.query(Keyword).filter(Keyword.name == keyword_name).first()
        if not keyword:
            return False

        user_keyword = (
            self.db.query(UserKeyword)
            .filter(
                UserKeyword.user_id == user.id, UserKeyword.keyword_id == keyword.id
            )
            .first()
        )

        if user_keyword:
            self.db.delete(user_keyword)
            self.db.commit()
            return True
        return False

    def get_user_keywords(self, slack_user_id: str) -> List[UserKeyword]:
        user = self.user_service.get_or_create_user(slack_user_id)
        return self.db.query(UserKeyword).filter(UserKeyword.user_id == user.id).all()

    def subscribe_author(
        self, slack_user_id: str, author_name: str
    ) -> Optional[UserAuthor]:
        user = self.user_service.get_or_create_user(slack_user_id)
        author = self.db.query(Author).filter(Author.name == author_name).first()
        if not author:
            author = Author(name=author_name)
            self.db.add(author)
            self.db.flush()

        user_author = (
            self.db.query(UserAuthor)
            .filter(UserAuthor.user_id == user.id, UserAuthor.author_id == author.id)
            .first()
        )

        if user_author:
            return None  # Already subscribed

        new_user_author = UserAuthor(user_id=user.id, author_id=author.id)
        self.db.add(new_user_author)
        self.db.commit()
        self.db.refresh(new_user_author)
        return new_user_author

    def unsubscribe_author(self, slack_user_id: str, author_name: str) -> bool:
        user = self.user_service.get_or_create_user(slack_user_id)
        author = self.db.query(Author).filter(Author.name == author_name).first()
        if not author:
            return False

        user_author = (
            self.db.query(UserAuthor)
            .filter(UserAuthor.user_id == user.id, UserAuthor.author_id == author.id)
            .first()
        )

        if user_author:
            self.db.delete(user_author)
            self.db.commit()
            return True
        return False

    def get_user_authors(self, slack_user_id: str) -> List[UserAuthor]:
        user = self.user_service.get_or_create_user(slack_user_id)
        return self.db.query(UserAuthor).filter(UserAuthor.user_id == user.id).all()
