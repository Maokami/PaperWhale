from apscheduler.schedulers.asyncio import AsyncIOScheduler # Changed to AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from app.db.database import SQLALCHEMY_DATABASE_URL, SessionLocal
from app.services.scholar_service import ScholarService
from app.services.slack_service import SlackService
from app.services.paper_service import PaperService
from app.db.models import UserKeyword, Keyword, Paper
from app.db.schemas import PaperCreate
from datetime import datetime
import asyncio

jobstores = {
    'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URL)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

async def check_for_new_papers_async():
    db = SessionLocal()
    slack_service = SlackService()
    try:
        scholar_service = ScholarService()
        user_keywords = db.query(UserKeyword).all()
        for user_keyword in user_keywords:
            keyword = db.query(Keyword).filter(Keyword.id == user_keyword.keyword_id).first()
            if keyword:
                print(f"Checking for new papers for keyword: {keyword.name}")
                new_papers_data = scholar_service.search_new_papers(keyword.name)
                for paper_data in new_papers_data:
                    # Check for duplicates before saving
                    existing_paper = db.query(Paper).filter(
                        (Paper.arxiv_id == paper_data.get("arxiv_id")) | (Paper.url == paper_data.get("url"))
                    ).first()

                    if not existing_paper:
                        paper_create = PaperCreate(
                            title=paper_data.get("title", "N/A"),
                            url=paper_data.get("url", "#"),
                            summary=paper_data.get("summary", "N/A"),
                            published_date=paper_data.get("published_date"),
                            arxiv_id=paper_data.get("arxiv_id"),
                            author_names=paper_data.get("authors", []),
                            keyword_names=[keyword.name] # Add the keyword that triggered the search
                        )
                        paper_service = PaperService(db)
                        new_paper = paper_service.create_paper(paper_create)

                        await slack_service.send_new_paper_notification(
                            user_id=user_keyword.user_id,
                            paper_title=new_paper.title,
                            paper_url=new_paper.url,
                            summary=new_paper.summary or 'N/A',
                            authors=", ".join([author.name for author in new_paper.authors]),
                            keywords=", ".join([keyword.name for keyword in new_paper.keywords])
                        )
                    else:
                        print(f"Paper already exists: {existing_paper.title}")
    finally:
        db.close()

async def start_scheduler(): # Made async
    scheduler.start()
    scheduler.add_job(check_for_new_papers_async, 'interval', minutes=60, id='new_paper_check', replace_existing=True)

async def shutdown_scheduler(): # Made async
    scheduler.shutdown()