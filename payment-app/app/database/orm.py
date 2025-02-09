import logging
import os

from typing import List

from dotenv import load_dotenv, find_dotenv

from sqlalchemy import Boolean, Float, String, create_engine, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class DatabaseManager(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    load_dotenv(find_dotenv())

    sync_engine = create_engine(
        os.getenv('POSTGRE_URL'),
        echo=True
    )

    sync_session = sessionmaker(bind=sync_engine)

    @classmethod
    def create_tables(cls) -> bool | None:
        try:
            with cls.sync_engine.begin() as connection:
                cls.metadata.create_all(connection)
                return True
        except Exception as e:
            logging.error(f'Error in create_tables creating tables: {e}')
            return False

    @classmethod
    def insert_entry(cls, **kwargs) -> bool:
        try:
            with cls.sync_session() as session:
                instance = cls(**kwargs)
                session.add(instance)
                session.commit()
                return True
        except Exception as e:
            logging.error(f"Error in insert_entry: {e}")
            return False

    @classmethod
    def get_entry(cls, **kwargs) -> object | bool:
        try:
            with cls.sync_session() as session:
                instance = session.query(cls).filter_by(**kwargs).first()
                return instance if instance else False
        except Exception as e:
            logging.error(f"Error in get_entry: {e}")
            return False

    @classmethod
    def get_entries(cls, **kwargs) -> list | bool:
        try:
            with cls.sync_session() as session:
                query = session.query(cls)
                if kwargs:
                    query = query.filter_by(**kwargs).limit(20)
                instances = query.all()
                return instances if instances else False
        except Exception as e:
            logging.error(f"Error in get_entries: {e}")
            return False


class User(DatabaseManager):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
    accounts: Mapped[List['Account']] = relationship()

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'is_admin': self.is_admin,
            'accounts': self.accounts,
        }


class Account(DatabaseManager):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[float] = mapped_column(Float, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    payments: Mapped[List['Payment']] = relationship()

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'balance': self.balance,
            'user_id': self.user_id,
            'payments': self.payments,
        }


class Payment(DatabaseManager):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    signature: Mapped[str] = mapped_column(String, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'transaction_id': self.uuid,
            'account_id': self.account_id,
            'amount': self.amount,
            'signature': self.signature,
        }
