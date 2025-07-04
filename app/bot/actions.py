from slack_bolt.async_app import AsyncApp
from app.db.database import get_db
from app.services.paper_service import PaperService
from app.services.user_subscription_service import UserSubscriptionService
from app.services.user_service import UserService
from app.db.schemas import PaperCreate
from datetime import datetime

def register_actions(app: AsyncApp):
    @app.view("summarize_paper_modal")
    async def handle_summarize_paper_modal_submission(ack, body, client, logger):
        await ack()
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        paper_id_str = state_values["paper_id_block"]["paper_id_input"]["value"]

        try:
            paper_id = int(paper_id_str)
            db = next(get_db())
            paper_service = PaperService(db)
            summary = await paper_service.summarize_paper(paper_id, user_id)

            if summary:
                await client.chat_postMessage(
                    channel=user_id,
                    text=f"*논문 ID {paper_id} 요약:*\n\n{summary}"
                )
            else:
                await client.chat_postMessage(
                    channel=user_id,
                    text=f"논문 ID {paper_id}를 찾을 수 없습니다."
                )
        except ValueError as e:
            logger.error(f"Value error: {e}")
            await client.chat_postMessage(
                channel=user_id,
                text=str(e)
            )
        except Exception as e:
            logger.error(f"Failed to summarize paper: {e}")
            await client.chat_postMessage(
                channel=user_id,
                text="논문 요약에 실패했습니다. 다시 시도해주세요."
            )

    @app.view("register_api_key_modal")
    async def handle_register_api_key_modal_submission(ack, body, client, logger):
        await ack()
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        api_key = state_values["api_key_block"]["api_key_input"]["value"]

        try:
            db = next(get_db())
            user_service = UserService(db)
            user_service.update_api_key(user_id, api_key)

            await client.chat_postMessage(
                channel=user_id,
                text="API Key가 성공적으로 등록되었습니다!"
            )
        except Exception as e:
            logger.error(f"Failed to register API key: {e}")
            await client.chat_postMessage(
                channel=user_id,
                text="API Key 등록에 실패했습니다. 다시 시도해주세요."
            )

    @app.view("add_paper_modal")
    async def handle_add_paper_modal_submission(ack, body, client, logger):
        await ack()
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        title = state_values["paper_title_block"]["paper_title_input"]["value"]
        url = state_values["paper_url_block"]["paper_url_input"]["value"]
        authors_str = state_values["paper_authors_block"]["paper_authors_input"]["value"]
        keywords_str = state_values["paper_keywords_block"]["paper_keywords_input"]["value"]
        summary = state_values["paper_summary_block"]["paper_summary_input"]["value"]
        published_date_str = state_values["paper_published_date_block"]["paper_published_date_input"]["value"]
        arxiv_id = state_values["paper_arxiv_id_block"]["paper_arxiv_id_input"]["value"]

        author_names = [name.strip() for name in authors_str.split(',') if name.strip()] if authors_str else []
        keyword_names = [name.strip() for name in keywords_str.split(',') if name.strip()] if keywords_str else []

        published_date = None
        if published_date_str:
            try:
                published_date = datetime.strptime(published_date_str, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid date format: {published_date_str}")
                # Optionally, send a message to the user about the invalid date
                await client.chat_postMessage(
                    channel=user_id,
                    text="논문 추가에 실패했습니다. 발행일 형식이 올바르지 않습니다 (YYYY-MM-DD)."
                )
                return

        try:
            db = next(get_db())
            paper_service = PaperService(db)
            paper_create = PaperCreate(
                title=title,
                url=url,
                summary=summary,
                published_date=published_date,
                arxiv_id=arxiv_id,
                author_names=author_names,
                keyword_names=keyword_names
            )
            new_paper = paper_service.create_paper(paper_create)

            await client.chat_postMessage(
                channel=user_id,
                text=f"논문 '{new_paper.title}'이(가) 성공적으로 추가되었습니다!"
            )
        except Exception as e:
            logger.error(f"Failed to add paper: {e}")
            await client.chat_postMessage(
                channel=user_id,
                text="논문 추가에 실패했습니다. 다시 시도해주세요."
            )

    @app.view("search_paper_modal")
    async def handle_search_paper_modal_submission(ack, body, client, logger):
        await ack()
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        search_query = state_values["search_query_block"]["search_query_input"]["value"]

        try:
            db = next(get_db())
            paper_service = PaperService(db)
            found_papers = paper_service.search_papers(search_query)

            if found_papers:
                blocks = [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*{len(found_papers)}개의 논문을 찾았습니다:*"}
                    }
                ]
                for paper in found_papers:
                    authors = ", ".join([author.name for author in paper.authors])
                    keywords = ", ".join([keyword.name for keyword in paper.keywords])
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*<{paper.url}|{paper.title}>*\n*저자:* {authors}\n*키워드:* {keywords}\n*요약:* {paper.summary or 'N/A'}\n*발행일:* {paper.published_date.strftime('%Y-%m-%d') if paper.published_date else 'N/A'}"
                            }
                        }
                    )
                    blocks.append({"type": "divider"})
                await client.chat_postMessage(
                    channel=user_id,
                    blocks=blocks
                )
            else:
                await client.chat_postMessage(
                    channel=user_id,
                    text=f"'{search_query}'(으)로 검색된 논문이 없습니다."
                )
        except Exception as e:
            logger.error(f"Failed to search papers: {e}")
            await client.chat_postMessage(
                channel=user_id,
                text="논문 검색에 실패했습니다. 다시 시도해주세요."
            )

    @app.view("register_keyword_modal")
    async def handle_register_keyword_modal_submission(ack, body, client, logger):
        await ack()
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        keyword_name = state_values["keyword_name_block"]["keyword_name_input"]["value"]

        try:
            db = next(get_db())
            user_subscription_service = UserSubscriptionService(db)
            new_subscription = user_subscription_service.subscribe_keyword(user_id, keyword_name)

            if new_subscription:
                await client.chat_postMessage(
                    channel=user_id,
                    text=f"키워드 '{keyword_name}'이(가) 성공적으로 등록되었습니다!"
                )
            else:
                await client.chat_postMessage(
                    channel=user_id,
                    text=f"키워드 '{keyword_name}'은(는) 이미 등록되어 있습니다."
                )
        except Exception as e:
            logger.error(f"Failed to register keyword: {e}")
            await client.chat_postMessage(
                channel=user_id,
                text="키워드 등록에 실패했습니다. 다시 시도해주세요."
            )
