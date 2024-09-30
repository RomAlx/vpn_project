from sqlalchemy.orm import Session
from backend.models import User

from backend.objects.Database import session


class UserRepository:

    @staticmethod
    def update_or_create_user(tg_id: int, first_name: str, balance: float = 0.0) -> User:
        user = UserRepository.get_user_by_tg_id(tg_id)
        if user:
            user.first_name = first_name
        else:
            user = User(tg_id=tg_id, first_name=first_name, balance=balance)
            session.add(user)

        session.commit()  # Сохранение изменений в базе данных
        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_tg_id(tg_id: int) -> User:
        return session.query(User).filter(User.tg_id == tg_id).first()

    @staticmethod
    def update_user_balance(user_id: int, new_balance: float):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            user.balance = new_balance
            session.commit()
        return user

    @staticmethod
    def delete_user(user_id: int):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            session.delete(user)
            session.commit()

    @staticmethod
    def list_all_users():
        return session.query(User).all()