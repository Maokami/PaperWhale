from slack_bolt.async_app import AsyncApp
from app.services.ai_service import AIService  # AIService 임포트


def register_commands(app: AsyncApp, ai_service: AIService):
    @app.command("/논문-요약")
    async def summarize_paper_command(ack, body, client):
        await ack()
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "summarize_paper_modal",
                "title": {"type": "plain_text", "text": "논문 요약"},
                "submit": {"type": "plain_text", "text": "요약"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "paper_id_block",
                        "label": {"type": "plain_text", "text": "논문 ID"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_id_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "요약할 논문의 ID를 입력하세요",
                            },
                        },
                    }
                ],
            },
        )

    @app.command("/api-key-등록")
    async def register_api_key_command(ack, body, client):
        await ack()
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "register_api_key_modal",
                "title": {"type": "plain_text", "text": "API Key 등록"},
                "submit": {"type": "plain_text", "text": "등록"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "api_key_block",
                        "label": {"type": "plain_text", "text": "API Key"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "api_key_input",
                            "placeholder": {"type": "plain_text", "text": "sk-..."},
                        },
                    }
                ],
            },
        )

    @app.command("/논문-추가")
    async def add_paper_command(ack, body, client):
        await ack()
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "add_paper_modal",
                "title": {"type": "plain_text", "text": "논문 추가"},
                "submit": {"type": "plain_text", "text": "추가"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "paper_title_block",
                        "label": {"type": "plain_text", "text": "제목"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_title_input",
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_url_block",
                        "label": {"type": "plain_text", "text": "URL"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_url_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "https://arxiv.org/abs/2301.00001",
                            },
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_bibtex_block",
                        "label": {"type": "plain_text", "text": "BibTeX (선택 사항)"},
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "paper_bibtex_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "@article{...}",
                            },
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_authors_block",
                        "label": {"type": "plain_text", "text": "저자 (쉼표로 구분)"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_authors_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "John Doe, Jane Smith",
                            },
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_keywords_block",
                        "label": {"type": "plain_text", "text": "키워드 (쉼표로 구분)"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_keywords_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "PL, Type Systems",
                            },
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_summary_block",
                        "label": {"type": "plain_text", "text": "요약"},
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "paper_summary_input",
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_published_date_block",
                        "label": {"type": "plain_text", "text": "발행일 (YYYY-MM-DD)"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_published_date_input",
                            "placeholder": {"type": "plain_text", "text": "2023-01-01"},
                        },
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "block_id": "paper_arxiv_id_block",
                        "label": {
                            "type": "plain_text",
                            "text": "arXiv ID (예: 2301.00001)",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "paper_arxiv_id_input",
                            "placeholder": {"type": "plain_text", "text": "2301.00001"},
                        },
                        "optional": True,
                    },
                ],
            },
        )

    @app.command("/논문-검색")
    async def search_paper_command(ack, body, client):
        await ack()
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "search_paper_modal",
                "title": {"type": "plain_text", "text": "논문 검색"},
                "submit": {"type": "plain_text", "text": "검색"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "search_query_block",
                        "label": {
                            "type": "plain_text",
                            "text": "검색어 (제목, 저자, 키워드, 요약)",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "search_query_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "검색어 입력",
                            },
                        },
                    }
                ],
            },
        )

    @app.command("/키워드-등록")
    async def register_keyword_command(ack, body, client):
        await ack()
        await client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "register_keyword_modal",
                "title": {"type": "plain_text", "text": "키워드 등록"},
                "submit": {"type": "plain_text", "text": "등록"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "keyword_name_block",
                        "label": {"type": "plain_text", "text": "등록할 키워드"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "keyword_name_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "예: Reinforcement Learning",
                            },
                        },
                    }
                ],
            },
        )

    @app.command("/요약")
    async def summarize_text_command(ack, say, command):
        await ack()
        text_to_summarize = command["text"]
        if not text_to_summarize:
            await say("요약할 텍스트를 입력해주세요. 예: `/요약 긴 텍스트...`")
            return

        try:
            # AIService를 사용하여 텍스트 요약
            summary = await ai_service.summarize_text(text_to_summarize)
            await say(f"요약 결과:\n{summary}")
        except Exception as e:
            await say(f"텍스트 요약 중 오류가 발생했습니다: {e}")
