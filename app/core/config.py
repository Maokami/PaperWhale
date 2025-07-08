from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SLACK_BOT_TOKEN: str
    SLACK_SIGNING_SECRET: str
    SLACK_APP_TOKEN: str
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    GEMINI_API_KEY: str | None = None


settings = Settings()
