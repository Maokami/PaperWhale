from pydantic import BaseModel, HttpUrl, root_validator, ValidationError
from datetime import datetime
from typing import List, Optional, Dict, Any


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
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None
    published_date: Optional[datetime] = None
    arxiv_id: Optional[str] = None


class PaperCreate(PaperBase):
    author_names: List[str] = []
    keyword_names: List[str] = []
    bibtex: Optional[str] = None

    @root_validator(pre=True)
    def check_required_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        title = values.get("title")
        url = values.get("url")
        bibtex = values.get("bibtex")

        if not bibtex and (not title or not url):
            raise ValueError(
                "Either bibtex must be provided, or both title and url must be provided."
            )
        return values


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
