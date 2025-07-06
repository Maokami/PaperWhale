from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from app.db.database import SQLALCHEMY_DATABASE_URL, SessionLocal
from app.services.scholar_service import ScholarService
from app.services.slack_service import SlackService
from app.services.paper_service import PaperService
from app.db.models import UserKeyword, Paper
from app.db.schemas import PaperCreate
from sqlalchemy.orm import joinedload
from collections import defaultdict

jobstores = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URL)}
executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
job_defaults = {"coalesce": False, "max_instances": 3}

scheduler = AsyncIOScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults
)


async def check_for_new_papers_async():
    db = SessionLocal()
    slack_service = SlackService()
    try:
        scholar_service = ScholarService()

        # Optimize query to fetch keywords and users together
        user_keywords = (
            db.query(UserKeyword)
            .options(joinedload(UserKeyword.keyword), joinedload(UserKeyword.user))
            .all()
        )

        keyword_to_users = defaultdict(list)
        for uk in user_keywords:
            if uk.keyword and uk.user:
                keyword_to_users[uk.keyword.name].append(uk.user.slack_user_id)

        for keyword_name, user_ids in keyword_to_users.items():
            print(f"Checking for new papers for keyword: {keyword_name}")
            new_papers_data = scholar_service.search_new_papers(keyword_name)
            for paper_data in new_papers_data:
                # Check for duplicates before saving
                existing_paper = (
                    db.query(Paper)
                    .filter(
                        (Paper.arxiv_id == paper_data.get("arxiv_id"))
                        | (Paper.url == paper_data.get("url"))
                    )
                    .first()
                )

                if not existing_paper:
                    paper_create = PaperCreate(
                        title=paper_data.get("title", "N/A"),
                        url=paper_data.get("url", "#"),
                        summary=paper_data.get("summary", "N/A"),
                        published_date=paper_data.get("published_date"),
                        arxiv_id=paper_data.get("arxiv_id"),
                        author_names=paper_data.get("authors", []),
                        keyword_names=[keyword_name],
                    )
                    paper_service = PaperService(db)
                    new_paper = paper_service.create_paper(paper_create)

                    for user_id in user_ids:
                        await slack_service.send_new_paper_notification(
                            user_id=user_id,
                            paper_title=new_paper.title,
                            paper_url=new_paper.url,
                            summary=new_paper.summary or "N/A",
                            authors=", ".join(
                                [author.name for author in new_paper.authors]
                            ),
                            keywords=", ".join(
                                [keyword.name for keyword in new_paper.keywords]
                            ),
                        )
                else:
                    print(f"Paper already exists: {existing_paper.title}")
    finally:
        db.close()


async def start_scheduler():
    scheduler.start()
    scheduler.add_job(
        check_for_new_papers_async,
        "interval",
        minutes=60,
        id="new_paper_check",
        replace_existing=True,
    )


async def shutdown_scheduler():
    scheduler.shutdown()
