from slack_bolt.async_app import AsyncApp
from app.core.config import settings
from app.bot.commands import register_commands
from app.bot.actions import register_actions
from concurrent.futures import ThreadPoolExecutor

# Initialize Slack Bolt app
slack_app = AsyncApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
    request_verification_enabled=False,
    executor=ThreadPoolExecutor(max_workers=5),
)

register_commands(slack_app)
register_actions(slack_app)


# Example Slack event listener (App Home Opened)
@slack_app.event("app_home_opened")
async def app_home_opened(ack, client, event):
    ack()
    user_id = event["user"]
    client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Welcome to PaperWhale, <@{user_id}>!* :whale:\n\nThis is your personal research assistant. You can use slash commands to manage papers, subscribe to keywords, and more.",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Available Commands:*\n- `/논문-추가`: Add a new paper to your archive.\n- `/논문-검색`: Search for papers in your archive.\n- `/키워드-등록`: Subscribe to a keyword for new paper alerts.",
                    },
                },
            ],
        },
    )
