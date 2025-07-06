from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    published_date = Column(DateTime, default=lambda: datetime.now(UTC))
    arxiv_id = Column(String, unique=True, nullable=True)  # For arXiv papers

    # Relationships
    authors = relationship("Author", secondary="paper_authors", back_populates="papers")
    keywords = relationship(
        "Keyword", secondary="paper_keywords", back_populates="papers"
    )


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    papers = relationship("Paper", secondary="paper_authors", back_populates="authors")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    papers = relationship(
        "Paper", secondary="paper_keywords", back_populates="keywords"
    )


class PaperAuthor(Base):
    __tablename__ = "paper_authors"
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)


class PaperKeyword(Base):
    __tablename__ = "paper_keywords"
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    slack_user_id = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, nullable=True)  # For AI services

    keywords = relationship("UserKeyword", back_populates="user")
    authors = relationship("UserAuthor", back_populates="user")


class UserKeyword(Base):
    __tablename__ = "user_keywords"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)

    user = relationship("User", back_populates="keywords")
    keyword = relationship("Keyword")


class UserAuthor(Base):
    __tablename__ = "user_authors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

    user = relationship("User", back_populates="authors")
    author = relationship("Author")
