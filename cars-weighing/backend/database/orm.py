import logging
import os

from dotenv import load_dotenv, find_dotenv

from sqlalchemy import DateTime, Text, Integer, Float, ForeignKey, create_engine
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class DatabaseManager(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    load_dotenv(find_dotenv())

    sync_engine = create_engine(
        os.getenv('DATABASE_URL'),
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
    def insert_entity(cls, **kwargs) -> bool | None:
        try:
            with cls.sync_session() as session:
                instance = cls(**kwargs)
                session.add(instance)
                session.commit()
                return True
        except Exception as e:
            logging.error(f"Error in insert_entity: {e}")
            return False

    @classmethod
    def get_entity(cls) -> list | None:
        try:
            with cls.sync_session() as session:
                applications = session.query(cls).all()
                return applications
        except Exception as e:
            logging.error(f"Error in get_entities: {e}")
            return None


class Train(DatabaseManager):
    __tablename__ = 'trains'

    id: Mapped[int] = mapped_column(primary_key=True)
    datetime: Mapped[DateTime] = mapped_column(DateTime)
    direction: Mapped[str] = mapped_column(Text)
    cars = relationship("Car", back_populates="train",
                        cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'datetime': self.datetime,
            'direction': self.direction,
            'cars': self.cars
        }


class Car(DatabaseManager):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(primary_key=True)
    train_id: Mapped[int] = mapped_column(Integer, ForeignKey('trains.id'))
    train = relationship("Train", back_populates="cars")
    weight: Mapped[float] = mapped_column(Float)
    carts = relationship("Cart", back_populates="car",
                         cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'traid_id': self.train_id,
            'weight': self.weight,
            'train_id': self.train_id,
            'carts': self.carts
        }


class Cart(DatabaseManager):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey('cars.id'))
    car = relationship("Car", back_populates="carts")
    axles = relationship("Axle", back_populates="cart",
                         cascade="all, delete-orphan")


class Axle(DatabaseManager):
    __tablename__ = 'axles'

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey('carts.id'))
    cart = relationship("Cart", back_populates="axles")
    weight: Mapped[float] = mapped_column(Float)
    speed: Mapped[float] = mapped_column(Float)
