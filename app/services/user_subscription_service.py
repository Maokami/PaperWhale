from sqlalchemy.orm import Session
from app.db.models import UserKeyword, UserAuthor, Keyword, Author
from app.db.schemas import UserKeywordCreate, UserAuthorCreate
from typing import List, Optional

class UserSubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def subscribe_keyword(self, user_id: str, keyword_name: str) -> Optional[UserKeyword]:
        keyword = self.db.query(Keyword).filter(Keyword.name == keyword_name).first()
        if not keyword:
            keyword = Keyword(name=keyword_name)
            self.db.add(keyword)
            self.db.flush()

        user_keyword = self.db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.keyword_id == keyword.id
        ).first()

        if user_keyword:
            return None # Already subscribed

        new_user_keyword = UserKeyword(user_id=user_id, keyword_id=keyword.id)
        self.db.add(new_user_keyword)
        self.db.commit()
        self.db.refresh(new_user_keyword)
        return new_user_keyword

    def unsubscribe_keyword(self, user_id: str, keyword_name: str) -> bool:
        keyword = self.db.query(Keyword).filter(Keyword.name == keyword_name).first()
        if not keyword:
            return False

        user_keyword = self.db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.keyword_id == keyword.id
        ).first()

        if user_keyword:
            self.db.delete(user_keyword)
            self.db.commit()
            return True
        return False

    def get_user_keywords(self, user_id: str) -> List[UserKeyword]:
        return self.db.query(UserKeyword).filter(UserKeyword.user_id == user_id).all()

    def subscribe_author(self, user_id: str, author_name: str) -> Optional[UserAuthor]:
        author = self.db.query(Author).filter(Author.name == author_name).first()
        if not author:
            author = Author(name=author_name)
            self.db.add(author)
            self.db.flush()

        user_author = self.db.query(UserAuthor).filter(
            UserAuthor.user_id == user_id,
            UserAuthor.author_id == author.id
        ).first()

        if user_author:
            return None # Already subscribed

        new_user_author = UserAuthor(user_id=user_id, author_id=author.id)
        self.db.add(new_user_author)
        self.db.commit()
        self.db.refresh(new_user_author)
        return new_user_author

    def unsubscribe_author(self, user_id: str, author_name: str) -> bool:
        author = self.db.query(Author).filter(Author.name == author_name).first()
        if not author:
            return False

        user_author = self.db.query(UserAuthor).filter(
            UserAuthor.user_id == user_id,
            UserAuthor.author_id == author.id
        ).first()

        if user_author:
            self.db.delete(user_author)
            self.db.commit()
            return True
        return False

    def get_user_authors(self, user_id: str) -> List[UserAuthor]:
        return self.db.query(UserAuthor).filter(UserAuthor.user_id == user_id).all()
