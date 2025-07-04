import logging
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from app.bot.app import slack_app
from app.core.config import settings
from app.db.database import init_db

logging.basicConfig(level=logging.DEBUG)

async def main():
    init_db()
    handler = AsyncSocketModeHandler(slack_app, settings.SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
