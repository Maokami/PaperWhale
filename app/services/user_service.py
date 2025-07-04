from sqlalchemy.orm import Session
from app.db import models, schemas

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, slack_user_id: str) -> models.User:
        user = self.db.query(models.User).filter(models.User.slack_user_id == slack_user_id).first()
        if not user:
            user = models.User(slack_user_id=slack_user_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_api_key(self, slack_user_id: str, api_key: str) -> models.User:
        user = self.get_or_create_user(slack_user_id)
        user.api_key = api_key
        self.db.commit()
        self.db.refresh(user)
        return user
