from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import event
import os
#from config import DATABASE_URL as DATABASE_URL_CONFIG

DATABASE_URL = os.getenv("DATABASE_URL")
#DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL_CONFIG)
#DATABASE_URL = "sqlite+aiosqlite:///database.sqlite3"
engine = create_async_engine(url=DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(25), nullable=False)
    tg_id = mapped_column(BigInteger, nullable=False)

class Module(Base):
    __tablename__ = 'modules'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

class Word(Base):
    __tablename__ = 'words'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(25), nullable=False)
    translation: Mapped[str] = mapped_column(String(25), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey('modules.id'), nullable=False)

async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(async_main())
        