from slack_sdk.web.async_client import AsyncWebClient # Changed to AsyncWebClient
from slack_sdk.errors import SlackApiError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SlackService:
    def __init__(self):
        self.client = AsyncWebClient(token=settings.SLACK_BOT_TOKEN)

    async def send_message(self, channel: str, text: str, blocks: list = None):
        try:
            await self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
        except SlackApiError as e:
            logger.error(f"Error sending message to Slack: {e.response['error']}")

    async def send_new_paper_notification(self, user_id: str, paper_title: str, paper_url: str, summary: str, authors: str, keywords: str):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""새로운 논문이 발견되었습니다! :rocket:\n*<{paper_url}|{paper_title}>*"""
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"""*저자:*
{authors}"""
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"""*키워드:*
{keywords}"""
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""*요약:*
{summary}"""
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "논문 보기",
                            "emoji": True
                        },
                        "url": paper_url,
                        "action_id": "view_paper_button"
                    }
                ]
            }
        ]
        await self.send_message(channel=user_id, text=f"새로운 논문: {paper_title}", blocks=blocks)
