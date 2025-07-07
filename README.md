# PaperWhale

[![CI](https://github.com/maokami/PaperWhale/actions/workflows/ci.yaml/badge.svg)](https://github.com/maokami/PaperWhale/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/maokami/PaperWhale/graph/badge.svg?token=YOUR_CODECOV_TOKEN)](https://codecov.io/gh/maokami/PaperWhale)

PaperWhale is an intelligent Slack bot designed to help researchers and academics manage and discover new academic papers. It integrates with arXiv to fetch new research, allows users to subscribe to keywords and authors for personalized alerts, and can even summarize papers using AI.

## ✨ Features

*   **Automated Paper Discovery:** Periodically searches arXiv for new papers based on user-subscribed keywords.
*   **Personalized Notifications:** Sends direct Slack messages to users when new papers matching their subscriptions are found.
*   **Paper Management:** Users can add, search, and manage papers within their personal archive.
*   **Keyword & Author Subscriptions:** Subscribe to specific research keywords or authors to stay updated.
*   **AI Summarization:** Summarize academic papers using OpenAI's language models (requires user-provided OpenAI API key).
*   **FastAPI Backend:** Provides a robust API for managing data and handling Slack interactions.
*   **Socket Mode Support:** Easily run the bot in development environments without exposing a public endpoint.

## 🚀 Technologies Used

*   **Backend Framework:** FastAPI
*   **Slack Integration:** `slack_bolt`
*   **Database:** SQLAlchemy (ORM) with SQLite (default) or PostgreSQL support
*   **Scheduler:** APScheduler
*   **Paper Data Source:** arXiv API (`arxiv` library)
*   **AI Integration:** OpenAI API (`openai` library)
*   **Dependency Management:** `uv`
*   **Testing:** `pytest`, `pytest-cov`
*   **Code Quality:** `ruff`, `mypy`

## ⚙️ Setup & Installation

### Prerequisites

*   Python 3.11+
*   `uv` (recommended for dependency management): Install with `pip install uv`
*   A Slack Workspace where you can create a new Slack App.
*   An OpenAI API Key (optional, for AI summarization feature).

### Slack App Configuration

1.  **Create a New Slack App:** Go to [api.slack.com/apps](https://api.slack.com/apps) and click "Create New App". Choose "From scratch".
2.  **App Name & Workspace:** Give your app a name (e.g., "PaperWhale") and select your development Slack Workspace.
3.  **Basic Information:**
    *   **Install App to Workspace:** Navigate to "Install App" under "Settings" and click "Install to Workspace". Authorize the app. This will generate your `SLACK_BOT_TOKEN`.
    *   **Bot Token Scopes:** Under "OAuth & Permissions", add the following Bot Token Scopes:
        *   `app_mentions:read`
        *   `channels:history`
        *   `chat:write`
        *   `commands`
        *   `groups:history`
        *   `im:history`
        *   `mpim:history`
        *   `users:read`
        *   `users:read.email`
    *   **Event Subscriptions:** Under "Event Subscriptions", enable events and set the Request URL to `YOUR_PUBLIC_URL/slack/events` (if running in API mode) or enable Socket Mode. Add `app_home_opened` to "Subscribe to bot events".
    *   **Slash Commands:** Under "Slash Commands", create the following commands:
        *   `/논문-추가` (Request URL: `YOUR_PUBLIC_URL/slack/events` or enable Socket Mode)
        *   `/논문-검색` (Request URL: `YOUR_PUBLIC_URL/slack/events` or enable Socket Mode)
        *   `/키워드-등록` (Request URL: `YOUR_PUBLIC_URL/slack/events` or enable Socket Mode)
    *   **App-Level Tokens (for Socket Mode):** Under "Basic Information" -> "App-Level Tokens", generate a new token with `connections:write` scope. This will be your `SLACK_APP_TOKEN`.
    *   **Signing Secret:** Under "Basic Information", find your "Signing Secret".

### Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```dotenv
SLACK_BOT_TOKEN=xoxb-YOUR_BOT_TOKEN
SLACK_SIGNING_SECRET=YOUR_SIGNING_SECRET
SLACK_APP_TOKEN=xapp-YOUR_APP_TOKEN # Only needed for Socket Mode
DATABASE_URL=sqlite:///./sql_app.db # Or your PostgreSQL connection string
GEMINI_API_KEY=YOUR_GEMINI_API_KEY # Optional, for AI summarization
```

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/maokami/PaperWhale.git
    cd PaperWhale
    ```
2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    uv pip install -r requirements.txt
    uv pip install -r requirements-dev.txt
    ```
3.  **Initialize the database:**
    ```bash
    python create_db.py
    ```

## 🏃 Running the Application

You can run PaperWhale in two modes:

### 1. API Mode (for production or public deployment)

This mode requires a publicly accessible URL for Slack to send events to. You can use tools like `ngrok` for local development.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Make sure your Slack App's Request URL for Event Subscriptions and Slash Commands points to `http://YOUR_PUBLIC_URL/slack/events`.

### 2. Socket Mode (for local development without public URL)

Socket Mode allows your bot to connect directly to Slack's servers, bypassing the need for a public URL.

```bash
python run_socket_mode.py
```

Ensure you have configured `SLACK_APP_TOKEN` in your `.env` file and enabled Socket Mode in your Slack App settings.

## 🤖 Usage (Slack Commands)

Once the bot is running and installed in your Slack workspace, you can interact with it using slash commands:

*   `/논문-추가`: Add a new paper to your archive.
*   `/논문-검색`: Search for papers in your archive by title, summary, author, or keyword.
*   `/키워드-등록`: Subscribe to a keyword to receive notifications for new papers.

## 📂 Project Structure

```
PaperWhale/
├── app/
│   ├── api/             # FastAPI API endpoints
│   │   └── main.py      # Main API application
│   ├── bot/             # Slack bot logic
│   │   ├── actions.py   # Slack interactive actions
│   │   ├── app.py       # Slack Bolt app initialization
│   │   ├── commands.py  # Slack slash command handlers
│   │   └── events.py    # Slack event handlers (e.g., app_home_opened)
│   ├── core/            # Core configurations and utilities
│   │   ├── config.py    # Environment variable loading
│   │   └── scheduler.py # APScheduler setup and paper check job
│   ├── db/              # Database related files
│   │   ├── database.py  # SQLAlchemy engine and session setup
│   │   ├── models.py    # SQLAlchemy ORM models
│   │   └── schemas.py   # Pydantic schemas for data validation
│   ├── services/        # Business logic services
│   │   ├── ai_service.py           # OpenAI integration for summarization
│   │   ├── paper_service.py        # CRUD operations for papers
│   │   ├── scholar_service.py      # arXiv API integration
│   │   ├── slack_service.py        # Sending messages to Slack
│   │   ├── user_service.py         # User management
│   │   └── user_subscription_service.py # Keyword/author subscriptions
│   └── main.py          # Main entry point for combined FastAPI + Slack app
├── create_db.py         # Script to initialize the database
├── Dockerfile           # Docker build instructions
├── pyproject.toml       # Project metadata and dependencies (PEP 621)
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── run_socket_mode.py   # Entry point for running in Slack Socket Mode
└── tests/               # Unit and integration tests
```

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## 📄 License

This project is licensed under the MIT License.
