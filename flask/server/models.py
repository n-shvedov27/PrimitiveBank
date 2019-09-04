from sqlalchemy import Column, Integer, String, Boolean
from server import Session
from server import Base
from .exceptions import UserNotFoundException, UserIsBlockedException, NotEnoughMoneyException
from sqlalchemy.exc import SQLAlchemyError

from typing import Dict


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)

    unique_number = Column(String(36), nullable=False, index=True, unique=True)
    fio = Column(String(64), nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    holds = Column(Integer, nullable=False, default=0)
    status = Column(Boolean, nullable=False)

    @staticmethod
    def increase_balance(unique_number, increase_value) -> Dict:
        session = Session()
        try:
            session.connection(execution_options={'isolation_level': 'READ COMMITTED'})
            user = session.query(User).filter_by(unique_number=unique_number).with_for_update().one()
            if user is None:
                raise UserNotFoundException("User not found")
            if not user.status:
                raise UserIsBlockedException("User is blocked")
            user.balance += increase_value

            session.commit()
            user_info = user.serialize()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

        return user_info

    @staticmethod
    def substract_balance(unique_number, substract_value) -> Dict:
        session = Session()
        try:
            session.connection(execution_options={'isolation_level': 'READ COMMITTED'})
            user = session.query(User).filter_by(unique_number=unique_number).with_for_update().one()
            if user is None:
                raise UserNotFoundException("Not found user with unique number: {}".format(unique_number))
            if not user.status:
                raise UserIsBlockedException("User is blocked")

            if user.balance - user.holds - substract_value >= 0:
                user.holds += substract_value
                session.commit()
                user_info = user.serialize()
            else:
                raise NotEnoughMoneyException("Not enough money")
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

        return user_info

    def serialize(self):
        serialized_user = {
            'unique_number': self.unique_number,
            'fio': self.fio,
            'balance': self.balance,
            'holds': self.holds,
            'status': self.status
        }
        return serialized_user
