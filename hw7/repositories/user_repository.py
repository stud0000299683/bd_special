from typing import Type, List

from sqlalchemy.orm import Session
from ..models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Type[User] | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Type[User] | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self) -> list[Type[User]]:
        return self.db.query(User).all()

    def create(self, email: str, username: str, full_name: str) -> User:
        user = User(email=email, username=username, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, full_name: str) -> User:
        user = self.get_by_id(user_id)
        if user:
            user.full_name = full_name
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
