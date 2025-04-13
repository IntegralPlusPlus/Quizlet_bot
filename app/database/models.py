from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import event
import os

DATABASE_URL = "sqlite+aiosqlite:///database.sqlite3"
engine = create_async_engine(url=DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

class Module(Base):
    __tablename__ = 'modules'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

class Word(Base):
    __tablename__ = 'words'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(25))
    translation: Mapped[str] = mapped_column(String(25))
    module_id: Mapped[int] = mapped_column(ForeignKey('modules.id'))

async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        