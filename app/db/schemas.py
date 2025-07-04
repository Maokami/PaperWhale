from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional

class AuthorBase(BaseModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int

    class Config:
        from_attributes = True

class KeywordBase(BaseModel):
    name: str

class KeywordCreate(KeywordBase):
    pass

class Keyword(KeywordBase):
    id: int

    class Config:
        from_attributes = True

class PaperBase(BaseModel):
    title: str
    url: HttpUrl
    summary: Optional[str] = None
    published_date: Optional[datetime] = None
    arxiv_id: Optional[str] = None

class PaperCreate(PaperBase):
    author_names: List[str] = []
    keyword_names: List[str] = []

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None
    published_date: Optional[datetime] = None
    arxiv_id: Optional[str] = None
    author_names: Optional[List[str]] = None
    keyword_names: Optional[List[str]] = None

class Paper(PaperBase):
    id: int
    authors: List[Author] = []
    keywords: List[Keyword] = []

    class Config:
        from_attributes = True

class UserKeywordBase(BaseModel):
    user_id: str
    keyword_id: int

class UserKeywordCreate(UserKeywordBase):
    pass

class UserKeyword(UserKeywordBase):
    id: int
    keyword: Keyword

    class Config:
        from_attributes = True

class UserAuthorBase(BaseModel):
    user_id: str
    author_id: int

class UserAuthorCreate(UserAuthorBase):
    pass

class UserAuthor(UserAuthorBase):
    id: int
    author: Author

    class Config:
        from_attributes = True