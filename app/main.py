from fastapi import Request
from slack_bolt.adapter.fastapi import SlackRequestHandler
from app.api.main import app as api_app
from app.bot.app import slack_app

# Mount the API app
app = api_app

# Create a SlackRequestHandler
slack_handler = SlackRequestHandler(slack_app)

# Slack Bolt endpoint
@app.post("/slack/events")
async def slack_events(req: Request):
    return await slack_handler.handle(req)