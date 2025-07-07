import arxiv
from sqlalchemy.orm import Session
from app.db.models import Paper, Author, Keyword, PaperAuthor, PaperKeyword
from app.db.schemas import PaperCreate, PaperUpdate
from app.services.ai_service import AIService
from app.services.user_service import UserService
from typing import List, Optional
from sqlalchemy import or_
from datetime import datetime, UTC


class PaperService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    async def summarize_paper(self, paper_id: int, slack_user_id: str) -> Optional[str]:
        paper = self.get_paper(paper_id)
        if not paper:
            return None

        if (
            paper.summary and len(paper.summary) > 10
        ):  # Don't re-summarize if already summarized
            return paper.summary

        user = self.user_service.get_or_create_user(slack_user_id)
        if not user.api_key:
            raise ValueError("User API key is not set.")

        if not paper.arxiv_id:
            raise ValueError("Paper does not have an arXiv ID.")

        try:
            search = arxiv.Search(id_list=[paper.arxiv_id])
            paper_result = next(search.results())
            text_to_summarize = paper_result.summary
        except StopIteration:
            raise ValueError(f"Could not find paper with arXiv ID: {paper.arxiv_id}")

        ai_service = AIService(user.api_key)
        summary = await ai_service.summarize_text(
            text_to_summarize, length_instruction="in three sentences"
        )
        paper.summary = summary
        self.db.commit()
        return summary

    def get_paper(self, paper_id: int) -> Optional[Paper]:
        return self.db.query(Paper).filter(Paper.id == paper_id).first()

    def get_papers(self, skip: int = 0, limit: int = 100) -> List[Paper]:
        return self.db.query(Paper).offset(skip).limit(limit).all()

    def get_paper_by_url_or_arxiv_id(
        self, url: Optional[str] = None, arxiv_id: Optional[str] = None
    ) -> Optional[Paper]:
        if not url and not arxiv_id:
            return None
        query = self.db.query(Paper)
        if url:
            query = query.filter(Paper.url == url)
        if arxiv_id:
            query = query.filter(
                or_(query.expression.clauses, Paper.arxiv_id == arxiv_id)
            )
        return query.first()

    def create_paper(self, paper: PaperCreate) -> Paper:
        db_paper = Paper(
            title=paper.title,
            url=str(paper.url),  # Convert HttpUrl to string
            summary=paper.summary,
            published_date=paper.published_date
            if paper.published_date
            else datetime.now(UTC),
            arxiv_id=paper.arxiv_id,
        )
        self.db.add(db_paper)
        self.db.flush()  # Flush to get the paper ID before adding relationships

        self._add_authors_to_paper(db_paper, paper.author_names)
        self._add_keywords_to_paper(db_paper, paper.keyword_names)

        self.db.commit()
        self.db.refresh(db_paper)
        return db_paper

    def update_paper(self, paper_id: int, paper: PaperUpdate) -> Optional[Paper]:
        db_paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if not db_paper:
            return None

        for var, value in paper.model_dump(exclude_unset=True).items():
            if var == "author_names":
                # Clear existing authors and add new ones
                self.db.query(PaperAuthor).filter(
                    PaperAuthor.paper_id == paper_id
                ).delete()
                self._add_authors_to_paper(db_paper, value)
            elif var == "keyword_names":
                # Clear existing keywords and add new ones
                self.db.query(PaperKeyword).filter(
                    PaperKeyword.paper_id == paper_id
                ).delete()
                self._add_keywords_to_paper(db_paper, value)
            elif var == "url":
                setattr(db_paper, var, str(value))  # Convert HttpUrl to string
            else:
                setattr(db_paper, var, value)

        self.db.commit()
        self.db.refresh(db_paper)
        return db_paper

    def delete_paper(self, paper_id: int):
        db_paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if db_paper:
            self.db.delete(db_paper)
            self.db.commit()
            return True
        return False

    def search_papers(self, query: str) -> List[Paper]:
        search_query = f"%{query.lower()}%"
        return (
            self.db.query(Paper)
            .join(Paper.authors, isouter=True)
            .join(Paper.keywords, isouter=True)
            .filter(
                or_(
                    Paper.title.ilike(search_query),
                    Paper.summary.ilike(search_query),
                    Author.name.ilike(search_query),
                    Keyword.name.ilike(search_query),
                )
            )
            .distinct()
            .all()
        )

    def _get_or_create_author(self, author_name: str) -> Author:
        author = self.db.query(Author).filter(Author.name == author_name).first()
        if not author:
            author = Author(name=author_name)
            self.db.add(author)
            self.db.flush()
        return author

    def _get_or_create_keyword(self, keyword_name: str) -> Keyword:
        keyword = self.db.query(Keyword).filter(Keyword.name == keyword_name).first()
        if not keyword:
            keyword = Keyword(name=keyword_name)
            self.db.add(keyword)
            self.db.flush()
        return keyword

    def _add_authors_to_paper(self, db_paper: Paper, author_names: List[str]):
        for name in author_names:
            author = self._get_or_create_author(name)
            db_paper.authors.append(author)

    def _add_keywords_to_paper(self, db_paper: Paper, keyword_names: List[str]):
        for name in keyword_names:
            keyword = self._get_or_create_keyword(name)
            db_paper.keywords.append(keyword)
